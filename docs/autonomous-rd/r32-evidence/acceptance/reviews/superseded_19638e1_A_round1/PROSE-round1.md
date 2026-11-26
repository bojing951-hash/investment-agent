# 语义审查复算记录 — Audit-R32 正式使用验收 · A 问 · Round-1

| 项 | 内容 |
|---|---|
| 席位 | semantic-audit-seat(零上下文独立席) |
| 审查者标识 | independent-zero-context-seat-r32-a-round1 |
| 审查日期 | 2026-11-24 |
| 受审对象 | 受审运行目录(20261123T145753Z_…)内 agent_judgment.json 全文(agent_declaration、l3、l4、reader_map、quality_gate_notes)与 MAP_REPORT.md 中的判断文字 |
| 代码印章(规程第 0 节披露,本席未核对) | 19638e1487e1e5729b9645ce621c3435d0635d08 |
| 裁决 | **UPHELD** — MAJOR 0 / MINOR 9 / NIT 11;must_fix 为空 |
| 复算计点 / 偏离 | 计点 1006 / 偏离 1(信息行 43 不计入) |

## 0. 结论速览与计数口径

### 0.1 合规声明

- 只读: 受审运行目录、只读安装树(/tmp/r32-accept/final3)与冻结输入未写入、未移动、未删除任何文件;本席脚本与全部产出只写入 /tmp/r32-accept/review3/A_round1/。
- 未联网;未运行 ia_cli.py 的任何子命令;未调用 agent_judgment.record_semantic_verdict。
- 未读取规程第 2 节所列任何目录(含树内 docs/、其他运行目录、其他席位产出目录、research_archive、replay、install*、final* 中除只读安装树本身以外的目录)。
- 未委派子代理,全部复算由本席亲自完成;未索取、推测或依赖任何预审内容;与研判席、操作者无通信。
- 本记录引用的每个数字均来自 0.2 节所列只读面并注明出处(文件+键),未凭记忆或常识补数。

### 0.2 只读证据面

| 面 | 路径 | 本席用到的键 |
|---|---|---|
| 冻结快照 | /tmp/r32-accept/final3/data/daily/research_snapshot_20261123.json | series_store(92 条,每条 dates/values)、gate_a、research_as_of、target_date、facts(105 条,仅用于核对引用标签与 JGB 单点) |
| 冻结发布日历 | /tmp/r32-accept/final3/config/release_calendar.json | version=1.5.0、entries(18 条: obs_from/obs_to/not_published_as_of/first_publish_on_or_after;政策条目 decision_date/effective_on/target_value)、batches(6) |
| 指标注册表 | /tmp/r32-accept/final3/config/metric_registry.json | metric_id、frequency、unit、criticality(核对 JP_POLICY_TARGET 不在册) |
| 引擎面 | 受审运行目录 report.json | research_plan.point_values.cells(22 格×3 锚=66)、research_plan.turning_candidates.candidates(9)、research_plan.policy_event_clusters、steps[60] S5_compare 信封、steps[61] 相似检索面信封(事后块/差距/符号一致率)、agent_judgment.contract_verification |
| 证据索引 | 受审运行目录 evidence_index.json | 72 行(kind/metric_id/ref) |
| 研判席工单 | 受审运行目录 AGENT_SEAT_ENVELOPE.json | reader_map_contract.engine_faces(点值格、转折候选面 top9、政策事件簇、政策文件事实)、frozen_inputs(只读其清单,哈希未核对) |
| 读者报告 | 受审运行目录 MAP_REPORT.md | 判断文字(走位、传导链、对质表、情景表、历史段)与引擎确定性表(地区×维度同步面、引擎转折候选面、政策官方记录面等) |
| 受审判断 | 受审运行目录 agent_judgment.json | 全文 |

### 0.3 锚点、截止日与发布规则

- 锚点: 12个月前=2025-11-23;3个月前=2026-08-23;最新一期=2026-11-23。研究截止日=2026-11-23(快照 research_as_of=2026-11-23T22:53:47+08:00;2026-11-23 为星期一)。
- 「当时可见」的判定: 观测的发布日≤锚日/决议日才算可见。冻结发布日历条目优先;无条目时用席位约定规则: 月频观测记当月 1 日;CPI/CORE_CPI 月末+13 天;CORE_PCE 月末+30 天;失业率月末+5 天;工业生产月末+15 天;欧元区 HICP 快报月末(终值+16 天,日历有条目者从条目);中国 CPI/PPI 月末+9 天;中国 PMI 月末;日本 CPI 月末+20 天;东京 CPI 月末前 1 天;JP_POLICY_RATE 为月均、记月初;季度 GDP 观测=统计季首日,发布=季末+29/35/45 天(美/欧/日);日频市场序列当日;DFF=观测次日;CN_LPR_1Y 观测日=发布日。
- 上述规则落在锚点上的检验方式: 锚点节每个「最新可见观测」均由席位按上述可见性规则从 series_store 的 dates 独立推出(日历条目优先、其次约定规则),所得观测月再与判断档 observation_month、引擎格 observation_date 逐格比对(各 63 行);发布日本身不另设计点行。约定规则是席位的推定,非官方实录,凡有日历实录条目者一律以实录为准。
- 2025 年美国联邦政府停摆(冻结日历条目注记为 2025-10-01..11-12)造成的发布延误一律以日历实录为准: 2025-09 CPI 2025-10-24、2025-09 失业率 2025-11-20、2025-11 CPI 2025-12-18、2025-09 核心 PCE 2025-12-05、2025-09 工业生产 2025-12-03、2025Q3 GDP 2025-12-23 首发;2025-10 月 CPI 与失业率观测缺席(日历保守界条目 RC-2025SHUTDOWN-REST-CONSERVATIVE 覆盖 CPI/CORE_CPI/CORE_PCE/UNEMPLOYMENT/NFP/AHE/INDPRO 的 2025-09..2025-10 观测)。
- 政策日: 生效日取序列值变更日(DFEDTARU 2025-12-11、2026-09-17;ECB_DFR/ECB_MRO 2026-06-17、2026-09-16);日本央行决议日、生效日与目标值取冻结日历实录;美联储与欧央行决议日在冻结日历无实录,判断档按引擎惯例(美联储=生效日前一日,欧央行=生效日前上一个周四)回推并标【推断】,本席按同一惯例独立回推核对。

### 0.4 计点口径

- 一行=一个可独立直算的数值、日期、方向词、标签或缺席判定。计点条件: 判断档或引擎面有可比的报告值,且直算值与报告值按报告展示精度相等(比率类容差 0.05,事后块 0.01)才记「一致」,否则记「偏离」。
- 全台账唯一「偏离」即按上条规则判出: 引擎转折候选面 CORE_CPI 行的 Δ,面值 -0.3767、未舍入直算 -0.3768,相差 0.0000789,超过四位小数的半单位(0.00005)。该行属读者报告的引擎渲染面,判断档正文未引用;处置与定级见第 6 节 MINOR-9。
- 报告侧无数值、仅席位直算的行只作信息记录(共 43 行: 同步面底层读数变化 36 行、转折候选窗 3 行、历史段标签三联在场 3 行、政策面距上次调整天数[判断档未给出] 1 行),不计入计点也不计入偏离。
- 计点行内的特殊形态(如实说明): 3 行为空值对空值(引擎格 derived_yoy_pct 因基期缺席为 null,席位直算同为不可得,按一致计);3 行为「缺席」判定(席位直算无已发布观测,报告侧记 absent);6 行「缺席特征已披露」以引擎 missing_features 所载原因为直算值、以判断档差异段是否披露该缺席为报告值;20 行「证据引用」为引用可解析性判定(直算值=该引用在 series_store 解析到的观测日与观测值,报告值=判断档引用串及其是否在证据索引内,不含数值比对);其余为数值、日期或标签的直算比对。
- 重复记录(如实说明): 2 个观测值(CPI 同比 2026-07=3.3039、核心 PCE 同比 2026-09=3.1212)在判断档两处被引用,台账按引用处各记一行(同名两行,直算值与报告值相同)。按「一行=一处比对」计入 1006 点;若按不同观测值去重则为 1004 点,两种口径下覆盖均远超规程最低点数,偏离数不变。
- 逐点台账 = points_all.jsonl,由本席脚本依次追加、未手工改写: s10_recompute.py 产出主体;s24_sync_labels.py 追加判断档同步标签 9 行并把 3 行「标签三联在场」降为信息行;s32_add_candidates.py 追加转折候选面 40 行(候选面 9 项×前值/后值/Δ/窗口=36 行、行序 1 行、判断档所引制造业PMI同比 2 行、「候选面最大美欧值」1 行);s34b_add_refs.py 追加证据引用 20 行;s38_policy_dates.py 追加政策面 32 计点行与 1 信息行;s40_add_c2_rows.py(最后一个改动台账的脚本)追加 C2 陈述的事后方向归纳 4 行(风险资产与 GOLD_F 各窗为正的窗数、DXY 三窗为负,直接自快照复算并与台账逐值对账),台账至此定稿为 1049 行;s41_disclose_dups.py 只在裁决文件的 notes 内补写上一条重复记录说明,不改台账与任何计数。本文件由 s35_build_prose.py 把两段固定文字(prose_head.md、prose_tail.md)与台账生成的表格拼装而成,表格逐行取自 points_all.jsonl,未经手工改写。

### 0.5 裁决依据摘要(与 VERDICT-round1.json 的 notes 逐字一致)

> 零上下文独立席 A 问 Round-1 裁决=UPHELD。复算: 从冻结快照 series_store(92 条)、冻结日历(18 条)、report.json 引擎面直算后与判断档比对,计点 1006、偏离 1(另 43 行仅作信息记录,不计入;另有 2 个观测值[CPI 同比 2026-07、核心 PCE 同比 2026-09]各因在判断档两处被引用而按引用处记两行,按观测值去重为 1004 点);覆盖锚点 275、月频 187(含引擎转折候选面 9 项的前值/后值/Δ/窗口与判断档所引候选值共 40 行)、日频 133、历史 297、同步面 45(引擎全维表 36 格+判断档通胀维标签 9 格)、其他 69(含判断档 L3/L4 证据引用 20 个不同引用逐一回查证据索引与序列库、政策面 32 行: 决议日/生效日/官方目标值/待生效/距上次调整与距研究截止天数)。唯一偏离在读者报告的引擎渲染面而非判断档文字: 候选面 CORE_CPI 行 Δ -0.3767 为两个四位小数端点之差(2.4462−2.8229),按未舍入值直算为 -0.3768,相差 0.0001(末位一个单位,小于端点自身的展示精度),方向与行序不变,记 MINOR。(1) 数字/日期/方向: 判断档序列级数字全部命中——锚点回贴 63 值、转折候选面前值/后值 9 项与判断档所引制造业PMI同比 -2.3904→1.0101、四地走位叙述、传导链数字、三转折与补选、历史事后 3/6/12 月 99 值与引擎事后块 48 值、C2 陈述的事后方向归纳 4 行(风险资产与 GOLD_F 各窗为正的窗数 15/15 与 14/15、DXY 两段各 3/3 窗为负)、符号一致率、类比距离/分位/贡献/差距、政策日期与目标值(冻结日历实录条目与按惯例回推的决议日)、官方记录面天数(距上次调整/距决议/距维持 60/66/24 天)、面板值(+25/+25/+67)与窗启在值口径(+50/+50/+75)、资产月窗、Gate A 清单;证据引用 20 个不同引用全部在本轮证据索引内,均可解析到不晚于截止日的序列观测(其中 2 个按『标签日=观测月末、序列观测日=月初』双标签解析,该双标签已由判断档披露)。(2) 缺席与口径: CPI 2026-10 同比缺 2025-10 基期,如实标不可得;JP_POLICY_TARGET 不在注册表=数据不可得,不以月均冒充目标值;CN_OMO_7D 过期(滞后 24 天)、换锚后无新观测、JP_POLICY_RATE 月均口径均已分列;Gate A=DEGRADED(核心缺口 0/非核心缺口 7/非核心降级 8)清单与快照逐项一致并已披露。(3) 截止纪律: 引用观测日均不晚于 2026-11-23,盘中快照说明与 research_as_of 相容;历史事后段均标『事后/非预测』,当时可知值逐项核验;三段同步性通胀维标签 9/9 与引擎面一致,全维引擎表紧随判断行渲染,不构成叙述与面冲突。(4) 证伪与情景: CPI 2.5/CORE_PCE 2.8/BEI_10Y 1.8 阈值及 HY_OAS 4.61、USDJPY、BRENT_F 均在库;截止日读数(CPI 同比 3.72@2026-09、CORE_PCE 3.12@2026-09、BEI_10Y 2.15@2026-11-20)未触发亦未证伪两情景,方向互补;契约验证 14/14(覆盖 C1 与 C3 陈述;C2 陈述的历史事后数字不在契约绑定范围,已由本席另行复算)、six_checks 16/16、map_checks 7/7 均 VERIFIED,无非 VERIFIED 项,unresolved_unbound 为空。(5) 未达 MAJOR 的主要问题(MINOR 9 条): 对质表四环一律『尚不能区分』偏保守——第1环区分指标 BRENT_F 月末首尾 +27.00%(72.48→92.05)与竞争解释『大体持平』相左,第4环主解释预期在同窗未获支持(USDJPY +1.82%);动机环『证据减弱』以美国 CPI 概括欧/日决议,而两地决议前可见的本地区通胀处回升段;资产环利率腿(12 个月,实际 +102bp)与资产腿(近 1 个月)混窗,未披露 12 个月窗 SPX +8.03%、NIKKEI225 +22.47% 与实际利率同向上行;历史段同步性引导词只覆盖通胀维;情景触发条件称『决议日见发布日历实录』而冻结日历无美联储/欧央行条目;C3 引用 USDCNY 未使用(12 个月 −6.19%);『美欧中通胀共振』中国腿为 PPI 而 CPI 同窗持平(1.3→1.2);季频 GDP 锚点为最新修订值未在判断档注明;读者报告引擎转折候选面 CORE_CPI 行的 Δ -0.3767 由舍入后的端点相减而得,未舍入直算为 -0.3768(差值舍入口径未注明,判断档正文未引用该 Δ)。另 NIT 11 条(逐日共动面未入档、推定发布日落在周末[东京 8 月读数 2026-08-30 为星期日;美国 CPI 两处推定发布日 2026-06-13 为星期六、2026-09-13 为星期日]、「四地最高通胀读数之一」未标口径、制造业PMI同比口径未标百分比、工业同比低点月份、欧元区「加速」非逐月递增、「最大」关系词口径、证据引用条数未标范围、美国 12 个月前锚的 GDP 较欧元区与日本早一季[2025Q3 因停摆延至 2025-12-23 首发而当时不可见,取值正确但未在判断档说明]、反例情景证伪阈值 1.8 未说明取值依据[距截止日读数 2.15 有 35 个基点,库内最近一次低于 1.8 为 2020-11-30])。上述问题均不改变结论的数字与方向(唯一数值偏离为末位舍入口径),亦无缺基期同比、相邻口径冒充、事后信息冒充当时可知或不可观测的证伪条件,故裁 UPHELD,must_fix 为空。引擎渲染面旁注(不计入问题清单): 判断档 quality_gate_notes 六条(盘中时点、对质面、证伪面、Gate A 数据面、政策口径披露、引擎缺口披露)原文仅存于 agent_judgment.json,未渲染入 MAP_REPORT.md、FULL_REPORT.md 与 report.md(部分内容由 reader_map 与 L3 文字间接带入),报告内『逐项见质量注记』实为指向判断档;披露本身在判断档内与引擎面一致。

## 1. 复算清单

### 1.1 分节计数

| 节 | 计点行 | 一致 | 偏离 | 信息行(不计入) |
|---|---|---|---|---|
| 锚点(三时点对照) | 275 | 275 | 0 | 0 |
| 月频 | 187 | 186 | 1 | 0 |
| 日频 | 133 | 133 | 0 | 0 |
| 历史段 | 297 | 297 | 0 | 3 |
| 同步面 | 45 | 45 | 0 | 36 |
| 其他 | 69 | 69 | 0 | 4 |
| 合计 | 1006 | 1005 | 1 | 43 |

### 1.2 逐点台账(出处键 / 直算值 / 报告值 / 一致与否)

#### 1.2.1 锚点(三时点对照)(计点 275 行: 一致 275、偏离 0;信息行 0)

| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|---|
| 1 | US_REAL_GDP@12m:value | series_store.US_REAL_GDP@2025-04-01 (pub 2025-07-29) | 23884.563 | 23884.563 | 一致 | judgment reader_map.regions[0].anchor_echo[0] |
| 2 | US_REAL_GDP@12m:obs_month | series_store.US_REAL_GDP dates | 2025-04 | 2025-04 | 一致 | judgment reader_map.regions[0].anchor_echo[0] |
| 3 | US_REAL_GDP@12m:engine_cell_value | report.json cells.US_REAL_GDP.anchors[12个月前].value | 23884.563 | 23884.563 | 一致 |  |
| 4 | US_REAL_GDP@12m:engine_cell_obs_month | report.json cells.US_REAL_GDP.anchors[12个月前].observation_date | 2025-04 | 2025-04 | 一致 |  |
| 5 | US_REAL_GDP@12m:yoy_vs_engine_cell | series_store US_REAL_GDP yoy(2025-04-01) | 2.4206 | 2.42 | 一致 | yoy_status=ok |
| 6 | US_REAL_GDP@3m:value | series_store.US_REAL_GDP@2026-04-01 (pub 2026-07-29) | 24408.011 | 24408.011 | 一致 | judgment reader_map.regions[0].anchor_echo[1] |
| 7 | US_REAL_GDP@3m:obs_month | series_store.US_REAL_GDP dates | 2026-04 | 2026-04 | 一致 | judgment reader_map.regions[0].anchor_echo[1] |
| 8 | US_REAL_GDP@3m:engine_cell_value | report.json cells.US_REAL_GDP.anchors[3个月前].value | 24408.011 | 24408.011 | 一致 |  |
| 9 | US_REAL_GDP@3m:engine_cell_obs_month | report.json cells.US_REAL_GDP.anchors[3个月前].observation_date | 2026-04 | 2026-04 | 一致 |  |
| 10 | US_REAL_GDP@3m:yoy_vs_engine_cell | series_store US_REAL_GDP yoy(2026-04-01) | 2.1916 | 2.19 | 一致 | yoy_status=ok |
| 11 | US_REAL_GDP@now:value | series_store.US_REAL_GDP@2026-07-01 (pub 2026-10-29) | 24611.077 | 24611.077 | 一致 | judgment reader_map.regions[0].anchor_echo[2] |
| 12 | US_REAL_GDP@now:obs_month | series_store.US_REAL_GDP dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[0].anchor_echo[2] |
| 13 | US_REAL_GDP@now:engine_cell_value | report.json cells.US_REAL_GDP.anchors[最新一期].value | 24611.077 | 24611.077 | 一致 |  |
| 14 | US_REAL_GDP@now:engine_cell_obs_month | report.json cells.US_REAL_GDP.anchors[最新一期].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 15 | US_REAL_GDP@now:yoy_vs_engine_cell | series_store US_REAL_GDP yoy(2026-07-01) | 2.0657 | 2.07 | 一致 | yoy_status=ok |
| 16 | UNEMPLOYMENT@12m:value | series_store.UNEMPLOYMENT@2025-09-01 (pub 2025-11-20) | 4.4 | 4.4 | 一致 | judgment reader_map.regions[0].anchor_echo[3] |
| 17 | UNEMPLOYMENT@12m:obs_month | series_store.UNEMPLOYMENT dates | 2025-09 | 2025-09 | 一致 | judgment reader_map.regions[0].anchor_echo[3] |
| 18 | UNEMPLOYMENT@12m:engine_cell_value | report.json cells.UNEMPLOYMENT.anchors[12个月前].value | 4.4 | 4.4 | 一致 |  |
| 19 | UNEMPLOYMENT@12m:engine_cell_obs_month | report.json cells.UNEMPLOYMENT.anchors[12个月前].observation_date | 2025-09 | 2025-09 | 一致 |  |
| 20 | UNEMPLOYMENT@3m:value | series_store.UNEMPLOYMENT@2026-07-01 (pub 2026-08-05) | 4.1 | 4.1 | 一致 | judgment reader_map.regions[0].anchor_echo[4] |
| 21 | UNEMPLOYMENT@3m:obs_month | series_store.UNEMPLOYMENT dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[0].anchor_echo[4] |
| 22 | UNEMPLOYMENT@3m:engine_cell_value | report.json cells.UNEMPLOYMENT.anchors[3个月前].value | 4.1 | 4.1 | 一致 |  |
| 23 | UNEMPLOYMENT@3m:engine_cell_obs_month | report.json cells.UNEMPLOYMENT.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 24 | UNEMPLOYMENT@now:value | series_store.UNEMPLOYMENT@2026-10-01 (pub 2026-11-05) | 4.1 | 4.1 | 一致 | judgment reader_map.regions[0].anchor_echo[5] |
| 25 | UNEMPLOYMENT@now:obs_month | series_store.UNEMPLOYMENT dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[0].anchor_echo[5] |
| 26 | UNEMPLOYMENT@now:engine_cell_value | report.json cells.UNEMPLOYMENT.anchors[最新一期].value | 4.1 | 4.1 | 一致 |  |
| 27 | UNEMPLOYMENT@now:engine_cell_obs_month | report.json cells.UNEMPLOYMENT.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 28 | INDPRO@12m:value | series_store.INDPRO@2025-08-01 (pub 2025-09-15) | 101.6247 | 101.6247 | 一致 | judgment reader_map.regions[0].anchor_echo[6] |
| 29 | INDPRO@12m:obs_month | series_store.INDPRO dates | 2025-08 | 2025-08 | 一致 | judgment reader_map.regions[0].anchor_echo[6] |
| 30 | INDPRO@12m:engine_cell_value | report.json cells.INDPRO.anchors[12个月前].value | 101.6247 | 101.6247 | 一致 |  |
| 31 | INDPRO@12m:engine_cell_obs_month | report.json cells.INDPRO.anchors[12个月前].observation_date | 2025-08 | 2025-08 | 一致 |  |
| 32 | INDPRO@12m:yoy_vs_engine_cell | series_store INDPRO yoy(2025-08-01) | 1.1887 | 1.19 | 一致 | yoy_status=ok |
| 33 | INDPRO@3m:value | series_store.INDPRO@2026-07-01 (pub 2026-08-15) | 103.1675 | 103.1675 | 一致 | judgment reader_map.regions[0].anchor_echo[7] |
| 34 | INDPRO@3m:obs_month | series_store.INDPRO dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[0].anchor_echo[7] |
| 35 | INDPRO@3m:engine_cell_value | report.json cells.INDPRO.anchors[3个月前].value | 103.1675 | 103.1675 | 一致 |  |
| 36 | INDPRO@3m:engine_cell_obs_month | report.json cells.INDPRO.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 37 | INDPRO@3m:yoy_vs_engine_cell | series_store INDPRO yoy(2026-07-01) | 1.2498 | 1.25 | 一致 | yoy_status=ok |
| 38 | INDPRO@now:value | series_store.INDPRO@2026-10-01 (pub 2026-11-15) | 103.3954 | 103.3954 | 一致 | judgment reader_map.regions[0].anchor_echo[8] |
| 39 | INDPRO@now:obs_month | series_store.INDPRO dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[0].anchor_echo[8] |
| 40 | INDPRO@now:engine_cell_value | report.json cells.INDPRO.anchors[最新一期].value | 103.3954 | 103.3954 | 一致 |  |
| 41 | INDPRO@now:engine_cell_obs_month | report.json cells.INDPRO.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 42 | INDPRO@now:yoy_vs_engine_cell | series_store INDPRO yoy(2026-10-01) | 2.1497 | 2.15 | 一致 | yoy_status=ok |
| 43 | CPI@12m:value | series_store.CPI@2025-09-01 (pub 2025-10-24) | 324.245 | 324.245 | 一致 | judgment reader_map.regions[0].anchor_echo[9] |
| 44 | CPI@12m:obs_month | series_store.CPI dates | 2025-09 | 2025-09 | 一致 | judgment reader_map.regions[0].anchor_echo[9] |
| 45 | CPI@12m:engine_cell_value | report.json cells.CPI.anchors[12个月前].value | 324.245 | 324.245 | 一致 |  |
| 46 | CPI@12m:engine_cell_obs_month | report.json cells.CPI.anchors[12个月前].observation_date | 2025-09 | 2025-09 | 一致 |  |
| 47 | CPI@12m:yoy_vs_engine_cell | series_store CPI yoy(2025-09-01) | 3.0226 | 3.02 | 一致 | yoy_status=ok |
| 48 | CPI@3m:value | series_store.CPI@2026-07-01 (pub 2026-08-13) | 332.813 | 332.813 | 一致 | judgment reader_map.regions[0].anchor_echo[10] |
| 49 | CPI@3m:obs_month | series_store.CPI dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[0].anchor_echo[10] |
| 50 | CPI@3m:engine_cell_value | report.json cells.CPI.anchors[3个月前].value | 332.813 | 332.813 | 一致 |  |
| 51 | CPI@3m:engine_cell_obs_month | report.json cells.CPI.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 52 | CPI@3m:yoy_vs_engine_cell | series_store CPI yoy(2026-07-01) | 3.3039 | 3.3 | 一致 | yoy_status=ok |
| 53 | CPI@now:value | series_store.CPI@2026-10-01 (pub 2026-11-13) | 337.476 | 337.476 | 一致 | judgment reader_map.regions[0].anchor_echo[11] |
| 54 | CPI@now:obs_month | series_store.CPI dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[0].anchor_echo[11] |
| 55 | CPI@now:engine_cell_value | report.json cells.CPI.anchors[最新一期].value | 337.476 | 337.476 | 一致 |  |
| 56 | CPI@now:engine_cell_obs_month | report.json cells.CPI.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 57 | CPI@now:yoy_vs_engine_cell | series_store CPI yoy(2026-10-01) | 不可得(null) | 不可得(null) | 一致 | yoy_status=no_same_period_base \| null handling |
| 58 | CORE_CPI@12m:value | series_store.CORE_CPI@2025-09-01 (pub 2025-10-24) | 330.418 | 330.418 | 一致 | judgment reader_map.regions[0].anchor_echo[12] |
| 59 | CORE_CPI@12m:obs_month | series_store.CORE_CPI dates | 2025-09 | 2025-09 | 一致 | judgment reader_map.regions[0].anchor_echo[12] |
| 60 | CORE_CPI@12m:engine_cell_value | report.json cells.CORE_CPI.anchors[12个月前].value | 330.418 | 330.418 | 一致 |  |
| 61 | CORE_CPI@12m:engine_cell_obs_month | report.json cells.CORE_CPI.anchors[12个月前].observation_date | 2025-09 | 2025-09 | 一致 |  |
| 62 | CORE_CPI@12m:yoy_vs_engine_cell | series_store CORE_CPI yoy(2025-09-01) | 3.02 | 3.02 | 一致 | yoy_status=ok |
| 63 | CORE_CPI@3m:value | series_store.CORE_CPI@2026-07-01 (pub 2026-08-13) | 336.789 | 336.789 | 一致 | judgment reader_map.regions[0].anchor_echo[13] |
| 64 | CORE_CPI@3m:obs_month | series_store.CORE_CPI dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[0].anchor_echo[13] |
| 65 | CORE_CPI@3m:engine_cell_value | report.json cells.CORE_CPI.anchors[3个月前].value | 336.789 | 336.789 | 一致 |  |
| 66 | CORE_CPI@3m:engine_cell_obs_month | report.json cells.CORE_CPI.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 67 | CORE_CPI@3m:yoy_vs_engine_cell | series_store CORE_CPI yoy(2026-07-01) | 2.4665 | 2.47 | 一致 | yoy_status=ok |
| 68 | CORE_CPI@now:value | series_store.CORE_CPI@2026-10-01 (pub 2026-11-13) | 339.9 | 339.9 | 一致 | judgment reader_map.regions[0].anchor_echo[14] |
| 69 | CORE_CPI@now:obs_month | series_store.CORE_CPI dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[0].anchor_echo[14] |
| 70 | CORE_CPI@now:engine_cell_value | report.json cells.CORE_CPI.anchors[最新一期].value | 339.9 | 339.9 | 一致 |  |
| 71 | CORE_CPI@now:engine_cell_obs_month | report.json cells.CORE_CPI.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 72 | CORE_CPI@now:yoy_vs_engine_cell | series_store CORE_CPI yoy(2026-10-01) | 不可得(null) | 不可得(null) | 一致 | yoy_status=no_same_period_base \| null handling |
| 73 | CORE_PCE@12m:value | series_store.CORE_PCE@2025-08-01 (pub 2025-09-30) | 126.646 | 126.646 | 一致 | judgment reader_map.regions[0].anchor_echo[15] |
| 74 | CORE_PCE@12m:obs_month | series_store.CORE_PCE dates | 2025-08 | 2025-08 | 一致 | judgment reader_map.regions[0].anchor_echo[15] |
| 75 | CORE_PCE@12m:engine_cell_value | report.json cells.CORE_PCE.anchors[12个月前].value | 126.646 | 126.646 | 一致 |  |
| 76 | CORE_PCE@12m:engine_cell_obs_month | report.json cells.CORE_PCE.anchors[12个月前].observation_date | 2025-08 | 2025-08 | 一致 |  |
| 77 | CORE_PCE@12m:yoy_vs_engine_cell | series_store CORE_PCE yoy(2025-08-01) | 2.8513 | 2.85 | 一致 | yoy_status=ok |
| 78 | CORE_PCE@3m:value | series_store.CORE_PCE@2026-06-01 (pub 2026-07-30) | 129.969 | 129.969 | 一致 | judgment reader_map.regions[0].anchor_echo[16] |
| 79 | CORE_PCE@3m:obs_month | series_store.CORE_PCE dates | 2026-06 | 2026-06 | 一致 | judgment reader_map.regions[0].anchor_echo[16] |
| 80 | CORE_PCE@3m:engine_cell_value | report.json cells.CORE_PCE.anchors[3个月前].value | 129.969 | 129.969 | 一致 |  |
| 81 | CORE_PCE@3m:engine_cell_obs_month | report.json cells.CORE_PCE.anchors[3个月前].observation_date | 2026-06 | 2026-06 | 一致 |  |
| 82 | CORE_PCE@3m:yoy_vs_engine_cell | series_store CORE_PCE yoy(2026-06-01) | 3.0412 | 3.04 | 一致 | yoy_status=ok |
| 83 | CORE_PCE@now:value | series_store.CORE_PCE@2026-09-01 (pub 2026-10-30) | 130.902 | 130.902 | 一致 | judgment reader_map.regions[0].anchor_echo[17] |
| 84 | CORE_PCE@now:obs_month | series_store.CORE_PCE dates | 2026-09 | 2026-09 | 一致 | judgment reader_map.regions[0].anchor_echo[17] |
| 85 | CORE_PCE@now:engine_cell_value | report.json cells.CORE_PCE.anchors[最新一期].value | 130.902 | 130.902 | 一致 |  |
| 86 | CORE_PCE@now:engine_cell_obs_month | report.json cells.CORE_PCE.anchors[最新一期].observation_date | 2026-09 | 2026-09 | 一致 |  |
| 87 | CORE_PCE@now:yoy_vs_engine_cell | series_store CORE_PCE yoy(2026-09-01) | 3.1212 | 3.12 | 一致 | yoy_status=ok |
| 88 | DFEDTARU@12m:value | series_store.DFEDTARU@2025-11-23 (pub 2025-11-23) | 4.0 | 4.0 | 一致 | judgment reader_map.regions[0].anchor_echo[18] |
| 89 | DFEDTARU@12m:obs_month | series_store.DFEDTARU dates | 2025-11 | 2025-11 | 一致 | judgment reader_map.regions[0].anchor_echo[18] |
| 90 | DFEDTARU@12m:engine_cell_value | report.json cells.DFEDTARU.anchors[12个月前].value | 4.0 | 4.0 | 一致 |  |
| 91 | DFEDTARU@12m:engine_cell_obs_month | report.json cells.DFEDTARU.anchors[12个月前].observation_date | 2025-11 | 2025-11 | 一致 |  |
| 92 | DFEDTARU@3m:value | series_store.DFEDTARU@2026-08-23 (pub 2026-08-23) | 3.75 | 3.75 | 一致 | judgment reader_map.regions[0].anchor_echo[19] |
| 93 | DFEDTARU@3m:obs_month | series_store.DFEDTARU dates | 2026-08 | 2026-08 | 一致 | judgment reader_map.regions[0].anchor_echo[19] |
| 94 | DFEDTARU@3m:engine_cell_value | report.json cells.DFEDTARU.anchors[3个月前].value | 3.75 | 3.75 | 一致 |  |
| 95 | DFEDTARU@3m:engine_cell_obs_month | report.json cells.DFEDTARU.anchors[3个月前].observation_date | 2026-08 | 2026-08 | 一致 |  |
| 96 | DFEDTARU@now:value | series_store.DFEDTARU@2026-11-23 (pub 2026-11-23) | 4.0 | 4.0 | 一致 | judgment reader_map.regions[0].anchor_echo[20] |
| 97 | DFEDTARU@now:obs_month | series_store.DFEDTARU dates | 2026-11 | 2026-11 | 一致 | judgment reader_map.regions[0].anchor_echo[20] |
| 98 | DFEDTARU@now:engine_cell_value | report.json cells.DFEDTARU.anchors[最新一期].value | 4.0 | 4.0 | 一致 |  |
| 99 | DFEDTARU@now:engine_cell_obs_month | report.json cells.DFEDTARU.anchors[最新一期].observation_date | 2026-11 | 2026-11 | 一致 |  |
| 100 | DFF@12m:value | series_store.DFF@2025-11-22 (pub 2025-11-23) | 3.88 | 3.88 | 一致 | judgment reader_map.regions[0].anchor_echo[21] |
| 101 | DFF@12m:obs_month | series_store.DFF dates | 2025-11 | 2025-11 | 一致 | judgment reader_map.regions[0].anchor_echo[21] |
| 102 | DFF@12m:engine_cell_value | report.json cells.DFF.anchors[12个月前].value | 3.88 | 3.88 | 一致 |  |
| 103 | DFF@12m:engine_cell_obs_month | report.json cells.DFF.anchors[12个月前].observation_date | 2025-11 | 2025-11 | 一致 |  |
| 104 | DFF@3m:value | series_store.DFF@2026-08-22 (pub 2026-08-23) | 3.63 | 3.63 | 一致 | judgment reader_map.regions[0].anchor_echo[22] |
| 105 | DFF@3m:obs_month | series_store.DFF dates | 2026-08 | 2026-08 | 一致 | judgment reader_map.regions[0].anchor_echo[22] |
| 106 | DFF@3m:engine_cell_value | report.json cells.DFF.anchors[3个月前].value | 3.63 | 3.63 | 一致 |  |
| 107 | DFF@3m:engine_cell_obs_month | report.json cells.DFF.anchors[3个月前].observation_date | 2026-08 | 2026-08 | 一致 |  |
| 108 | DFF@now:value | series_store.DFF@2026-11-19 (pub 2026-11-20) | 3.88 | 3.88 | 一致 | judgment reader_map.regions[0].anchor_echo[23] |
| 109 | DFF@now:obs_month | series_store.DFF dates | 2026-11 | 2026-11 | 一致 | judgment reader_map.regions[0].anchor_echo[23] |
| 110 | DFF@now:engine_cell_value | report.json cells.DFF.anchors[最新一期].value | 3.88 | 3.88 | 一致 |  |
| 111 | DFF@now:engine_cell_obs_month | report.json cells.DFF.anchors[最新一期].observation_date | 2026-11 | 2026-11 | 一致 |  |
| 112 | CN_PMI_MFG@12m:value | series_store.CN_PMI_MFG@2025-10-01 (pub 2025-10-31) | 49.0 | 49.0 | 一致 | judgment reader_map.regions[1].anchor_echo[0] |
| 113 | CN_PMI_MFG@12m:obs_month | series_store.CN_PMI_MFG dates | 2025-10 | 2025-10 | 一致 | judgment reader_map.regions[1].anchor_echo[0] |
| 114 | CN_PMI_MFG@12m:engine_cell_value | report.json cells.CN_PMI_MFG.anchors[12个月前].value | 49.0 | 49.0 | 一致 |  |
| 115 | CN_PMI_MFG@12m:engine_cell_obs_month | report.json cells.CN_PMI_MFG.anchors[12个月前].observation_date | 2025-10 | 2025-10 | 一致 |  |
| 116 | CN_PMI_MFG@3m:value | series_store.CN_PMI_MFG@2026-07-01 (pub 2026-07-31) | 49.2 | 49.2 | 一致 | judgment reader_map.regions[1].anchor_echo[1] |
| 117 | CN_PMI_MFG@3m:obs_month | series_store.CN_PMI_MFG dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[1].anchor_echo[1] |
| 118 | CN_PMI_MFG@3m:engine_cell_value | report.json cells.CN_PMI_MFG.anchors[3个月前].value | 49.2 | 49.2 | 一致 |  |
| 119 | CN_PMI_MFG@3m:engine_cell_obs_month | report.json cells.CN_PMI_MFG.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 120 | CN_PMI_MFG@now:value | series_store.CN_PMI_MFG@2026-10-01 (pub 2026-10-31) | 49.3 | 49.3 | 一致 | judgment reader_map.regions[1].anchor_echo[2] |
| 121 | CN_PMI_MFG@now:obs_month | series_store.CN_PMI_MFG dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[1].anchor_echo[2] |
| 122 | CN_PMI_MFG@now:engine_cell_value | report.json cells.CN_PMI_MFG.anchors[最新一期].value | 49.3 | 49.3 | 一致 |  |
| 123 | CN_PMI_MFG@now:engine_cell_obs_month | report.json cells.CN_PMI_MFG.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 124 | CN_CPI_YOY@12m:value | series_store.CN_CPI_YOY@2025-10-01 (pub 2025-11-09) | 0.2 | 0.2 | 一致 | judgment reader_map.regions[1].anchor_echo[3] |
| 125 | CN_CPI_YOY@12m:obs_month | series_store.CN_CPI_YOY dates | 2025-10 | 2025-10 | 一致 | judgment reader_map.regions[1].anchor_echo[3] |
| 126 | CN_CPI_YOY@12m:engine_cell_value | report.json cells.CN_CPI_YOY.anchors[12个月前].value | 0.2 | 0.2 | 一致 |  |
| 127 | CN_CPI_YOY@12m:engine_cell_obs_month | report.json cells.CN_CPI_YOY.anchors[12个月前].observation_date | 2025-10 | 2025-10 | 一致 |  |
| 128 | CN_CPI_YOY@3m:value | series_store.CN_CPI_YOY@2026-07-01 (pub 2026-08-09) | 0.5 | 0.5 | 一致 | judgment reader_map.regions[1].anchor_echo[4] |
| 129 | CN_CPI_YOY@3m:obs_month | series_store.CN_CPI_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[1].anchor_echo[4] |
| 130 | CN_CPI_YOY@3m:engine_cell_value | report.json cells.CN_CPI_YOY.anchors[3个月前].value | 0.5 | 0.5 | 一致 |  |
| 131 | CN_CPI_YOY@3m:engine_cell_obs_month | report.json cells.CN_CPI_YOY.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 132 | CN_CPI_YOY@now:value | series_store.CN_CPI_YOY@2026-10-01 (pub 2026-11-09) | 0.7 | 0.7 | 一致 | judgment reader_map.regions[1].anchor_echo[5] |
| 133 | CN_CPI_YOY@now:obs_month | series_store.CN_CPI_YOY dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[1].anchor_echo[5] |
| 134 | CN_CPI_YOY@now:engine_cell_value | report.json cells.CN_CPI_YOY.anchors[最新一期].value | 0.7 | 0.7 | 一致 |  |
| 135 | CN_CPI_YOY@now:engine_cell_obs_month | report.json cells.CN_CPI_YOY.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 136 | CN_PPI_YOY@12m:value | series_store.CN_PPI_YOY@2025-10-01 (pub 2025-11-09) | -2.1 | -2.1 | 一致 | judgment reader_map.regions[1].anchor_echo[6] |
| 137 | CN_PPI_YOY@12m:obs_month | series_store.CN_PPI_YOY dates | 2025-10 | 2025-10 | 一致 | judgment reader_map.regions[1].anchor_echo[6] |
| 138 | CN_PPI_YOY@12m:engine_cell_value | report.json cells.CN_PPI_YOY.anchors[12个月前].value | -2.1 | -2.1 | 一致 |  |
| 139 | CN_PPI_YOY@12m:engine_cell_obs_month | report.json cells.CN_PPI_YOY.anchors[12个月前].observation_date | 2025-10 | 2025-10 | 一致 |  |
| 140 | CN_PPI_YOY@3m:value | series_store.CN_PPI_YOY@2026-07-01 (pub 2026-08-09) | 3.5 | 3.5 | 一致 | judgment reader_map.regions[1].anchor_echo[7] |
| 141 | CN_PPI_YOY@3m:obs_month | series_store.CN_PPI_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[1].anchor_echo[7] |
| 142 | CN_PPI_YOY@3m:engine_cell_value | report.json cells.CN_PPI_YOY.anchors[3个月前].value | 3.5 | 3.5 | 一致 |  |
| 143 | CN_PPI_YOY@3m:engine_cell_obs_month | report.json cells.CN_PPI_YOY.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 144 | CN_PPI_YOY@now:value | series_store.CN_PPI_YOY@2026-10-01 (pub 2026-11-09) | 5.7 | 5.7 | 一致 | judgment reader_map.regions[1].anchor_echo[8] |
| 145 | CN_PPI_YOY@now:obs_month | series_store.CN_PPI_YOY dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[1].anchor_echo[8] |
| 146 | CN_PPI_YOY@now:engine_cell_value | report.json cells.CN_PPI_YOY.anchors[最新一期].value | 5.7 | 5.7 | 一致 |  |
| 147 | CN_PPI_YOY@now:engine_cell_obs_month | report.json cells.CN_PPI_YOY.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 148 | CN_POLICY_OVERNIGHT@now:value | series_store.CN_POLICY_OVERNIGHT@2026-11-23 (pub 2026-11-23) | 1.25 | 1.25 | 一致 | judgment reader_map.regions[1].anchor_echo[9] |
| 149 | CN_POLICY_OVERNIGHT@now:obs_month | series_store.CN_POLICY_OVERNIGHT dates | 2026-11 | 2026-11 | 一致 | judgment reader_map.regions[1].anchor_echo[9] |
| 150 | CN_POLICY_OVERNIGHT@now:engine_cell_value | report.json cells.CN_POLICY_OVERNIGHT.anchors[最新一期].value | 1.25 | 1.25 | 一致 |  |
| 151 | CN_POLICY_OVERNIGHT@now:engine_cell_obs_month | report.json cells.CN_POLICY_OVERNIGHT.anchors[最新一期].observation_date | 2026-11 | 2026-11 | 一致 |  |
| 152 | CN_OMO_7D@12m:value | series_store.CN_OMO_7D@2025-11-14 (pub 2025-11-14) | 1.4 | 1.4 | 一致 | judgment reader_map.regions[1].anchor_echo[10] |
| 153 | CN_OMO_7D@12m:obs_month | series_store.CN_OMO_7D dates | 2025-11 | 2025-11 | 一致 | judgment reader_map.regions[1].anchor_echo[10] |
| 154 | CN_OMO_7D@12m:engine_cell_value | report.json cells.CN_OMO_7D.anchors[12个月前].value | 1.4 | 1.4 | 一致 |  |
| 155 | CN_OMO_7D@12m:engine_cell_obs_month | report.json cells.CN_OMO_7D.anchors[12个月前].observation_date | 2025-11 | 2025-11 | 一致 |  |
| 156 | CN_OMO_7D@3m:value | series_store.CN_OMO_7D@2026-08-21 (pub 2026-08-21) | 1.4 | 1.4 | 一致 | judgment reader_map.regions[1].anchor_echo[11] |
| 157 | CN_OMO_7D@3m:obs_month | series_store.CN_OMO_7D dates | 2026-08 | 2026-08 | 一致 | judgment reader_map.regions[1].anchor_echo[11] |
| 158 | CN_OMO_7D@3m:engine_cell_value | report.json cells.CN_OMO_7D.anchors[3个月前].value | 1.4 | 1.4 | 一致 |  |
| 159 | CN_OMO_7D@3m:engine_cell_obs_month | report.json cells.CN_OMO_7D.anchors[3个月前].observation_date | 2026-08 | 2026-08 | 一致 |  |
| 160 | CN_OMO_7D@now:value | series_store.CN_OMO_7D@2026-10-30 (pub 2026-10-30) | 1.4 | 1.4 | 一致 | judgment reader_map.regions[1].anchor_echo[12] |
| 161 | CN_OMO_7D@now:obs_month | series_store.CN_OMO_7D dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[1].anchor_echo[12] |
| 162 | CN_OMO_7D@now:engine_cell_value | report.json cells.CN_OMO_7D.anchors[最新一期].value | 1.4 | 1.4 | 一致 |  |
| 163 | CN_OMO_7D@now:engine_cell_obs_month | report.json cells.CN_OMO_7D.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 164 | CN_LPR_1Y@12m:value | series_store.CN_LPR_1Y@2025-11-20 (pub 2025-11-20) | 3.0 | 3.0 | 一致 | judgment reader_map.regions[1].anchor_echo[13] |
| 165 | CN_LPR_1Y@12m:obs_month | series_store.CN_LPR_1Y dates | 2025-11 | 2025-11 | 一致 | judgment reader_map.regions[1].anchor_echo[13] |
| 166 | CN_LPR_1Y@12m:engine_cell_value | report.json cells.CN_LPR_1Y.anchors[12个月前].value | 3.0 | 3.0 | 一致 |  |
| 167 | CN_LPR_1Y@12m:engine_cell_obs_month | report.json cells.CN_LPR_1Y.anchors[12个月前].observation_date | 2025-11 | 2025-11 | 一致 |  |
| 168 | CN_LPR_1Y@3m:value | series_store.CN_LPR_1Y@2026-08-20 (pub 2026-08-20) | 3.0 | 3.0 | 一致 | judgment reader_map.regions[1].anchor_echo[14] |
| 169 | CN_LPR_1Y@3m:obs_month | series_store.CN_LPR_1Y dates | 2026-08 | 2026-08 | 一致 | judgment reader_map.regions[1].anchor_echo[14] |
| 170 | CN_LPR_1Y@3m:engine_cell_value | report.json cells.CN_LPR_1Y.anchors[3个月前].value | 3.0 | 3.0 | 一致 |  |
| 171 | CN_LPR_1Y@3m:engine_cell_obs_month | report.json cells.CN_LPR_1Y.anchors[3个月前].observation_date | 2026-08 | 2026-08 | 一致 |  |
| 172 | CN_LPR_1Y@now:value | series_store.CN_LPR_1Y@2026-11-20 (pub 2026-11-20) | 3.0 | 3.0 | 一致 | judgment reader_map.regions[1].anchor_echo[15] |
| 173 | CN_LPR_1Y@now:obs_month | series_store.CN_LPR_1Y dates | 2026-11 | 2026-11 | 一致 | judgment reader_map.regions[1].anchor_echo[15] |
| 174 | CN_LPR_1Y@now:engine_cell_value | report.json cells.CN_LPR_1Y.anchors[最新一期].value | 3.0 | 3.0 | 一致 |  |
| 175 | CN_LPR_1Y@now:engine_cell_obs_month | report.json cells.CN_LPR_1Y.anchors[最新一期].observation_date | 2026-11 | 2026-11 | 一致 |  |
| 176 | EA_REAL_GDP_YOY@12m:value | series_store.EA_REAL_GDP_YOY@2025-07-01 (pub 2025-11-04) | 1.11 | 1.11 | 一致 | judgment reader_map.regions[2].anchor_echo[0] |
| 177 | EA_REAL_GDP_YOY@12m:obs_month | series_store.EA_REAL_GDP_YOY dates | 2025-07 | 2025-07 | 一致 | judgment reader_map.regions[2].anchor_echo[0] |
| 178 | EA_REAL_GDP_YOY@12m:engine_cell_value | report.json cells.EA_REAL_GDP_YOY.anchors[12个月前].value | 1.11 | 1.11 | 一致 |  |
| 179 | EA_REAL_GDP_YOY@12m:engine_cell_obs_month | report.json cells.EA_REAL_GDP_YOY.anchors[12个月前].observation_date | 2025-07 | 2025-07 | 一致 |  |
| 180 | EA_REAL_GDP_YOY@3m:value | series_store.EA_REAL_GDP_YOY@2026-04-01 (pub 2026-08-04) | 1.19 | 1.19 | 一致 | judgment reader_map.regions[2].anchor_echo[1] |
| 181 | EA_REAL_GDP_YOY@3m:obs_month | series_store.EA_REAL_GDP_YOY dates | 2026-04 | 2026-04 | 一致 | judgment reader_map.regions[2].anchor_echo[1] |
| 182 | EA_REAL_GDP_YOY@3m:engine_cell_value | report.json cells.EA_REAL_GDP_YOY.anchors[3个月前].value | 1.19 | 1.19 | 一致 |  |
| 183 | EA_REAL_GDP_YOY@3m:engine_cell_obs_month | report.json cells.EA_REAL_GDP_YOY.anchors[3个月前].observation_date | 2026-04 | 2026-04 | 一致 |  |
| 184 | EA_REAL_GDP_YOY@now:value | series_store.EA_REAL_GDP_YOY@2026-07-01 (pub 2026-11-04) | 1.28 | 1.28 | 一致 | judgment reader_map.regions[2].anchor_echo[2] |
| 185 | EA_REAL_GDP_YOY@now:obs_month | series_store.EA_REAL_GDP_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[2].anchor_echo[2] |
| 186 | EA_REAL_GDP_YOY@now:engine_cell_value | report.json cells.EA_REAL_GDP_YOY.anchors[最新一期].value | 1.28 | 1.28 | 一致 |  |
| 187 | EA_REAL_GDP_YOY@now:engine_cell_obs_month | report.json cells.EA_REAL_GDP_YOY.anchors[最新一期].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 188 | EA_HICP_YOY@12m:value | series_store.EA_HICP_YOY@2025-10-01 (pub 2025-10-31) | 2.1 | 2.1 | 一致 | judgment reader_map.regions[2].anchor_echo[3] |
| 189 | EA_HICP_YOY@12m:obs_month | series_store.EA_HICP_YOY dates | 2025-10 | 2025-10 | 一致 | judgment reader_map.regions[2].anchor_echo[3] |
| 190 | EA_HICP_YOY@12m:engine_cell_value | report.json cells.EA_HICP_YOY.anchors[12个月前].value | 2.1 | 2.1 | 一致 |  |
| 191 | EA_HICP_YOY@12m:engine_cell_obs_month | report.json cells.EA_HICP_YOY.anchors[12个月前].observation_date | 2025-10 | 2025-10 | 一致 |  |
| 192 | EA_HICP_YOY@3m:value | series_store.EA_HICP_YOY@2026-07-01 (pub 2026-07-31) | 2.9 | 2.9 | 一致 | judgment reader_map.regions[2].anchor_echo[4] |
| 193 | EA_HICP_YOY@3m:obs_month | series_store.EA_HICP_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[2].anchor_echo[4] |
| 194 | EA_HICP_YOY@3m:engine_cell_value | report.json cells.EA_HICP_YOY.anchors[3个月前].value | 2.9 | 2.9 | 一致 |  |
| 195 | EA_HICP_YOY@3m:engine_cell_obs_month | report.json cells.EA_HICP_YOY.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 196 | EA_HICP_YOY@now:value | series_store.EA_HICP_YOY@2026-10-01 (pub 2026-10-31) | 4.0 | 4.0 | 一致 | judgment reader_map.regions[2].anchor_echo[5] |
| 197 | EA_HICP_YOY@now:obs_month | series_store.EA_HICP_YOY dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[2].anchor_echo[5] |
| 198 | EA_HICP_YOY@now:engine_cell_value | report.json cells.EA_HICP_YOY.anchors[最新一期].value | 4.0 | 4.0 | 一致 |  |
| 199 | EA_HICP_YOY@now:engine_cell_obs_month | report.json cells.EA_HICP_YOY.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 200 | ECB_MRO@12m:value | series_store.ECB_MRO@2025-06-11 (pub 2025-06-11) | 2.15 | 2.15 | 一致 | judgment reader_map.regions[2].anchor_echo[6] |
| 201 | ECB_MRO@12m:obs_month | series_store.ECB_MRO dates | 2025-06 | 2025-06 | 一致 | judgment reader_map.regions[2].anchor_echo[6] |
| 202 | ECB_MRO@12m:engine_cell_value | report.json cells.ECB_MRO.anchors[12个月前].value | 2.15 | 2.15 | 一致 |  |
| 203 | ECB_MRO@12m:engine_cell_obs_month | report.json cells.ECB_MRO.anchors[12个月前].observation_date | 2025-06 | 2025-06 | 一致 |  |
| 204 | ECB_MRO@3m:value | series_store.ECB_MRO@2026-06-17 (pub 2026-06-17) | 2.4 | 2.4 | 一致 | judgment reader_map.regions[2].anchor_echo[7] |
| 205 | ECB_MRO@3m:obs_month | series_store.ECB_MRO dates | 2026-06 | 2026-06 | 一致 | judgment reader_map.regions[2].anchor_echo[7] |
| 206 | ECB_MRO@3m:engine_cell_value | report.json cells.ECB_MRO.anchors[3个月前].value | 2.4 | 2.4 | 一致 |  |
| 207 | ECB_MRO@3m:engine_cell_obs_month | report.json cells.ECB_MRO.anchors[3个月前].observation_date | 2026-06 | 2026-06 | 一致 |  |
| 208 | ECB_MRO@now:value | series_store.ECB_MRO@2026-09-16 (pub 2026-09-16) | 2.65 | 2.65 | 一致 | judgment reader_map.regions[2].anchor_echo[8] |
| 209 | ECB_MRO@now:obs_month | series_store.ECB_MRO dates | 2026-09 | 2026-09 | 一致 | judgment reader_map.regions[2].anchor_echo[8] |
| 210 | ECB_MRO@now:engine_cell_value | report.json cells.ECB_MRO.anchors[最新一期].value | 2.65 | 2.65 | 一致 |  |
| 211 | ECB_MRO@now:engine_cell_obs_month | report.json cells.ECB_MRO.anchors[最新一期].observation_date | 2026-09 | 2026-09 | 一致 |  |
| 212 | ECB_DFR@12m:value | series_store.ECB_DFR@2025-06-11 (pub 2025-06-11) | 2.0 | 2.0 | 一致 | judgment reader_map.regions[2].anchor_echo[9] |
| 213 | ECB_DFR@12m:obs_month | series_store.ECB_DFR dates | 2025-06 | 2025-06 | 一致 | judgment reader_map.regions[2].anchor_echo[9] |
| 214 | ECB_DFR@12m:engine_cell_value | report.json cells.ECB_DFR.anchors[12个月前].value | 2.0 | 2.0 | 一致 |  |
| 215 | ECB_DFR@12m:engine_cell_obs_month | report.json cells.ECB_DFR.anchors[12个月前].observation_date | 2025-06 | 2025-06 | 一致 |  |
| 216 | ECB_DFR@3m:value | series_store.ECB_DFR@2026-06-17 (pub 2026-06-17) | 2.25 | 2.25 | 一致 | judgment reader_map.regions[2].anchor_echo[10] |
| 217 | ECB_DFR@3m:obs_month | series_store.ECB_DFR dates | 2026-06 | 2026-06 | 一致 | judgment reader_map.regions[2].anchor_echo[10] |
| 218 | ECB_DFR@3m:engine_cell_value | report.json cells.ECB_DFR.anchors[3个月前].value | 2.25 | 2.25 | 一致 |  |
| 219 | ECB_DFR@3m:engine_cell_obs_month | report.json cells.ECB_DFR.anchors[3个月前].observation_date | 2026-06 | 2026-06 | 一致 |  |
| 220 | ECB_DFR@now:value | series_store.ECB_DFR@2026-09-16 (pub 2026-09-16) | 2.5 | 2.5 | 一致 | judgment reader_map.regions[2].anchor_echo[11] |
| 221 | ECB_DFR@now:obs_month | series_store.ECB_DFR dates | 2026-09 | 2026-09 | 一致 | judgment reader_map.regions[2].anchor_echo[11] |
| 222 | ECB_DFR@now:engine_cell_value | report.json cells.ECB_DFR.anchors[最新一期].value | 2.5 | 2.5 | 一致 |  |
| 223 | ECB_DFR@now:engine_cell_obs_month | report.json cells.ECB_DFR.anchors[最新一期].observation_date | 2026-09 | 2026-09 | 一致 |  |
| 224 | JP_REAL_GDP_YOY@12m:value | series_store.JP_REAL_GDP_YOY@2025-07-01 (pub 2025-11-14) | 0.63 | 0.63 | 一致 | judgment reader_map.regions[3].anchor_echo[0] |
| 225 | JP_REAL_GDP_YOY@12m:obs_month | series_store.JP_REAL_GDP_YOY dates | 2025-07 | 2025-07 | 一致 | judgment reader_map.regions[3].anchor_echo[0] |
| 226 | JP_REAL_GDP_YOY@12m:engine_cell_value | report.json cells.JP_REAL_GDP_YOY.anchors[12个月前].value | 0.63 | 0.63 | 一致 |  |
| 227 | JP_REAL_GDP_YOY@12m:engine_cell_obs_month | report.json cells.JP_REAL_GDP_YOY.anchors[12个月前].observation_date | 2025-07 | 2025-07 | 一致 |  |
| 228 | JP_REAL_GDP_YOY@3m:value | series_store.JP_REAL_GDP_YOY@2026-04-01 (pub 2026-08-14) | 0.8 | 0.8 | 一致 | judgment reader_map.regions[3].anchor_echo[1] |
| 229 | JP_REAL_GDP_YOY@3m:obs_month | series_store.JP_REAL_GDP_YOY dates | 2026-04 | 2026-04 | 一致 | judgment reader_map.regions[3].anchor_echo[1] |
| 230 | JP_REAL_GDP_YOY@3m:engine_cell_value | report.json cells.JP_REAL_GDP_YOY.anchors[3个月前].value | 0.8 | 0.8 | 一致 |  |
| 231 | JP_REAL_GDP_YOY@3m:engine_cell_obs_month | report.json cells.JP_REAL_GDP_YOY.anchors[3个月前].observation_date | 2026-04 | 2026-04 | 一致 |  |
| 232 | JP_REAL_GDP_YOY@now:value | series_store.JP_REAL_GDP_YOY@2026-07-01 (pub 2026-11-14) | 1.16 | 1.16 | 一致 | judgment reader_map.regions[3].anchor_echo[2] |
| 233 | JP_REAL_GDP_YOY@now:obs_month | series_store.JP_REAL_GDP_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[3].anchor_echo[2] |
| 234 | JP_REAL_GDP_YOY@now:engine_cell_value | report.json cells.JP_REAL_GDP_YOY.anchors[最新一期].value | 1.16 | 1.16 | 一致 |  |
| 235 | JP_REAL_GDP_YOY@now:engine_cell_obs_month | report.json cells.JP_REAL_GDP_YOY.anchors[最新一期].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 236 | JP_CPI_YOY@12m:value | series_store.JP_CPI_YOY@2025-10-01 (pub 2025-11-20) | 2.99 | 2.99 | 一致 | judgment reader_map.regions[3].anchor_echo[3] |
| 237 | JP_CPI_YOY@12m:obs_month | series_store.JP_CPI_YOY dates | 2025-10 | 2025-10 | 一致 | judgment reader_map.regions[3].anchor_echo[3] |
| 238 | JP_CPI_YOY@12m:engine_cell_value | report.json cells.JP_CPI_YOY.anchors[12个月前].value | 2.99 | 2.99 | 一致 |  |
| 239 | JP_CPI_YOY@12m:engine_cell_obs_month | report.json cells.JP_CPI_YOY.anchors[12个月前].observation_date | 2025-10 | 2025-10 | 一致 |  |
| 240 | JP_CPI_YOY@3m:value | series_store.JP_CPI_YOY@2026-07-01 (pub 2026-08-20) | 1.97 | 1.97 | 一致 | judgment reader_map.regions[3].anchor_echo[4] |
| 241 | JP_CPI_YOY@3m:obs_month | series_store.JP_CPI_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[3].anchor_echo[4] |
| 242 | JP_CPI_YOY@3m:engine_cell_value | report.json cells.JP_CPI_YOY.anchors[3个月前].value | 1.97 | 1.97 | 一致 |  |
| 243 | JP_CPI_YOY@3m:engine_cell_obs_month | report.json cells.JP_CPI_YOY.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 244 | JP_CPI_YOY@now:value | series_store.JP_CPI_YOY@2026-10-01 (pub 2026-11-20) | 2.44 | 2.44 | 一致 | judgment reader_map.regions[3].anchor_echo[5] |
| 245 | JP_CPI_YOY@now:obs_month | series_store.JP_CPI_YOY dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[3].anchor_echo[5] |
| 246 | JP_CPI_YOY@now:engine_cell_value | report.json cells.JP_CPI_YOY.anchors[最新一期].value | 2.44 | 2.44 | 一致 |  |
| 247 | JP_CPI_YOY@now:engine_cell_obs_month | report.json cells.JP_CPI_YOY.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 248 | JP_CPI_TOKYO_YOY@3m:value | series_store.JP_CPI_TOKYO_YOY@2026-07-01 (pub 2026-07-30) | 1.85 | 1.85 | 一致 | judgment reader_map.regions[3].anchor_echo[6] |
| 249 | JP_CPI_TOKYO_YOY@3m:obs_month | series_store.JP_CPI_TOKYO_YOY dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[3].anchor_echo[6] |
| 250 | JP_CPI_TOKYO_YOY@3m:engine_cell_value | report.json cells.JP_CPI_TOKYO_YOY.anchors[3个月前].value | 1.85 | 1.85 | 一致 |  |
| 251 | JP_CPI_TOKYO_YOY@3m:engine_cell_obs_month | report.json cells.JP_CPI_TOKYO_YOY.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 252 | JP_CPI_TOKYO_YOY@now:value | series_store.JP_CPI_TOKYO_YOY@2026-10-01 (pub 2026-10-30) | 2.73 | 2.73 | 一致 | judgment reader_map.regions[3].anchor_echo[7] |
| 253 | JP_CPI_TOKYO_YOY@now:obs_month | series_store.JP_CPI_TOKYO_YOY dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[3].anchor_echo[7] |
| 254 | JP_CPI_TOKYO_YOY@now:engine_cell_value | report.json cells.JP_CPI_TOKYO_YOY.anchors[最新一期].value | 2.73 | 2.73 | 一致 |  |
| 255 | JP_CPI_TOKYO_YOY@now:engine_cell_obs_month | report.json cells.JP_CPI_TOKYO_YOY.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 256 | JP_POLICY_RATE@12m:value | series_store.JP_POLICY_RATE@2025-10-01 (pub 2025-11-05) | 0.477 | 0.477 | 一致 | judgment reader_map.regions[3].anchor_echo[8] |
| 257 | JP_POLICY_RATE@12m:obs_month | series_store.JP_POLICY_RATE dates | 2025-10 | 2025-10 | 一致 | judgment reader_map.regions[3].anchor_echo[8] |
| 258 | JP_POLICY_RATE@12m:engine_cell_value | report.json cells.JP_POLICY_RATE.anchors[12个月前].value | 0.477 | 0.477 | 一致 |  |
| 259 | JP_POLICY_RATE@12m:engine_cell_obs_month | report.json cells.JP_POLICY_RATE.anchors[12个月前].observation_date | 2025-10 | 2025-10 | 一致 |  |
| 260 | JP_POLICY_RATE@3m:value | series_store.JP_POLICY_RATE@2026-07-01 (pub 2026-08-05) | 0.978 | 0.978 | 一致 | judgment reader_map.regions[3].anchor_echo[9] |
| 261 | JP_POLICY_RATE@3m:obs_month | series_store.JP_POLICY_RATE dates | 2026-07 | 2026-07 | 一致 | judgment reader_map.regions[3].anchor_echo[9] |
| 262 | JP_POLICY_RATE@3m:engine_cell_value | report.json cells.JP_POLICY_RATE.anchors[3个月前].value | 0.978 | 0.978 | 一致 |  |
| 263 | JP_POLICY_RATE@3m:engine_cell_obs_month | report.json cells.JP_POLICY_RATE.anchors[3个月前].observation_date | 2026-07 | 2026-07 | 一致 |  |
| 264 | JP_POLICY_RATE@now:value | series_store.JP_POLICY_RATE@2026-10-01 (pub 2026-11-05) | 1.227 | 1.227 | 一致 | judgment reader_map.regions[3].anchor_echo[10] |
| 265 | JP_POLICY_RATE@now:obs_month | series_store.JP_POLICY_RATE dates | 2026-10 | 2026-10 | 一致 | judgment reader_map.regions[3].anchor_echo[10] |
| 266 | JP_POLICY_RATE@now:engine_cell_value | report.json cells.JP_POLICY_RATE.anchors[最新一期].value | 1.227 | 1.227 | 一致 |  |
| 267 | JP_POLICY_RATE@now:engine_cell_obs_month | report.json cells.JP_POLICY_RATE.anchors[最新一期].observation_date | 2026-10 | 2026-10 | 一致 |  |
| 268 | JP_POLICY_TARGET not in registry | snapshot series_store keys | False | absent | 一致 | judgment: plan metric not in registry |
| 269 | CN_POLICY_OVERNIGHT no obs before 3m anchor | series_store CN_POLICY_OVERNIGHT | 不可得(null) | absent | 一致 |  |
| 270 | CN_POLICY_OVERNIGHT first obs = 2026-11-02 | series_store CN_POLICY_OVERNIGHT dates | 2026-11-02 | 2026-11-02 | 一致 | headline: 2026-11-02 anchor switch |
| 271 | CN_POLICY_OVERNIGHT flat since first obs | series_store CN_POLICY_OVERNIGHT values | [1.25] | single value 1.25 | 一致 | flat at first observation |
| 272 | JP_CPI_TOKYO_YOY no published obs before 12m anchor | series_store JP_CPI_TOKYO_YOY | 不可得(null) | absent | 一致 |  |
| 273 | no observation after cutoff | series_store all series max date | 2026-11-23(SPX) | <=2026-11-23 | 一致 | research_as_of=2026-11-23T22:53:47+08:00 |
| 274 | snapshot research_as_of date | snapshot research_as_of | 2026-11-23 | 2026-11-23 | 一致 |  |
| 275 | snapshot target_date | snapshot target_date | 20261123 | 20261123 | 一致 |  |

#### 1.2.2 月频(计点 187 行: 一致 186、偏离 1;信息行 0)

| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|---|
| 276 | US GDP level 2025-04 | series_store US_REAL_GDP@2025-04 | 23884.563 | 23884.563 | 一致 | from_to narrative |
| 277 | US GDP level 2026-04 | series_store US_REAL_GDP@2026-04 | 24408.011 | 24408.011 | 一致 | from_to narrative |
| 278 | US GDP level 2026-07 | series_store US_REAL_GDP@2026-07 | 24611.077 | 24611.077 | 一致 | from_to narrative |
| 279 | US GDP yoy 2025-04 | series_store US_REAL_GDP 2025-04 vs 2024-04 | 2.4206 | 2.42 | 一致 | from_to narrative |
| 280 | US GDP yoy 2026-04 | series_store US_REAL_GDP 2026-04 vs 2025-04 | 2.1916 | 2.19 | 一致 | from_to narrative |
| 281 | US GDP yoy 2026-07 | series_store US_REAL_GDP 2026-07 vs 2025-07 | 2.0657 | 2.07 | 一致 | from_to narrative |
| 282 | UNEMP 2025-09 | series_store UNEMPLOYMENT@2025-09 | 4.4 | 4.4 | 一致 | from_to narrative |
| 283 | UNEMP 2026-07 | series_store UNEMPLOYMENT@2026-07 | 4.1 | 4.1 | 一致 | from_to narrative |
| 284 | UNEMP 2026-10 | series_store UNEMPLOYMENT@2026-10 | 4.1 | 4.1 | 一致 | from_to narrative |
| 285 | INDPRO level 2025-08 | series_store INDPRO@2025-08 | 101.6247 | 101.6247 | 一致 | from_to narrative |
| 286 | INDPRO level 2026-07 | series_store INDPRO@2026-07 | 103.1675 | 103.1675 | 一致 | from_to narrative |
| 287 | INDPRO level 2026-10 | series_store INDPRO@2026-10 | 103.3954 | 103.3954 | 一致 | from_to narrative |
| 288 | INDPRO yoy 2025-08 | series_store INDPRO 2025-08 vs 2024-08 | 1.1887 | 1.19 | 一致 | from_to narrative |
| 289 | INDPRO yoy 2026-07 | series_store INDPRO 2026-07 vs 2025-07 | 1.2498 | 1.25 | 一致 | from_to narrative |
| 290 | INDPRO yoy 2026-10 | series_store INDPRO 2026-10 vs 2025-10 | 2.1497 | 2.15 | 一致 | from_to narrative |
| 291 | CPI level 2025-09 | series_store CPI@2025-09 | 324.245 | 324.245 | 一致 | from_to narrative |
| 292 | CPI level 2026-07 | series_store CPI@2026-07 | 332.813 | 332.813 | 一致 | from_to narrative |
| 293 | CPI level 2026-10 | series_store CPI@2026-10 | 337.476 | 337.476 | 一致 | from_to narrative |
| 294 | CPI yoy 2025-09 | series_store CPI 2025-09 vs 2024-09 | 3.0226 | 3.02 | 一致 | from_to narrative |
| 295 | CPI yoy 2026-07 | series_store CPI 2026-07 vs 2025-07 | 3.3039 | 3.30 | 一致 | from_to narrative |
| 296 | CPI yoy 2026-10 | series_store CPI 2026-10 vs 2025-10 | 不可得(null) | 不可得(null) | 一致 | from_to narrative \| null handling |
| 297 | CORE_PCE level 2025-08 | series_store CORE_PCE@2025-08 | 126.646 | 126.646 | 一致 | from_to narrative |
| 298 | CORE_PCE level 2026-06 | series_store CORE_PCE@2026-06 | 129.969 | 129.969 | 一致 | from_to narrative |
| 299 | CORE_PCE level 2026-09 | series_store CORE_PCE@2026-09 | 130.902 | 130.902 | 一致 | from_to narrative |
| 300 | CORE_PCE yoy 2025-08 | series_store CORE_PCE 2025-08 vs 2024-08 | 2.8513 | 2.85 | 一致 | from_to narrative |
| 301 | CORE_PCE yoy 2026-06 | series_store CORE_PCE 2026-06 vs 2025-06 | 3.0412 | 3.04 | 一致 | from_to narrative |
| 302 | CORE_PCE yoy 2026-09 | series_store CORE_PCE 2026-09 vs 2025-09 | 3.1212 | 3.12 | 一致 | from_to narrative |
| 303 | EA GDP yoy 2025-07 | series_store EA_REAL_GDP_YOY@2025-07 | 1.11 | 1.11 | 一致 | from_to narrative |
| 304 | EA GDP yoy 2026-04 | series_store EA_REAL_GDP_YOY@2026-04 | 1.19 | 1.19 | 一致 | from_to narrative |
| 305 | EA GDP yoy 2026-07 | series_store EA_REAL_GDP_YOY@2026-07 | 1.28 | 1.28 | 一致 | from_to narrative |
| 306 | EA HICP 2025-10 | series_store EA_HICP_YOY@2025-10 | 2.1 | 2.1 | 一致 | from_to narrative |
| 307 | EA HICP 2026-07 | series_store EA_HICP_YOY@2026-07 | 2.9 | 2.9 | 一致 | from_to narrative |
| 308 | EA HICP 2026-10 | series_store EA_HICP_YOY@2026-10 | 4.0 | 4.0 | 一致 | from_to narrative |
| 309 | JP GDP yoy 2025-07 | series_store JP_REAL_GDP_YOY@2025-07 | 0.63 | 0.63 | 一致 | from_to narrative |
| 310 | JP GDP yoy 2026-04 | series_store JP_REAL_GDP_YOY@2026-04 | 0.8 | 0.80 | 一致 | from_to narrative |
| 311 | JP GDP yoy 2026-07 | series_store JP_REAL_GDP_YOY@2026-07 | 1.16 | 1.16 | 一致 | from_to narrative |
| 312 | JP CPI yoy 2025-10 | series_store JP_CPI_YOY@2025-10 | 2.99 | 2.99 | 一致 | from_to narrative |
| 313 | JP CPI yoy 2026-07 | series_store JP_CPI_YOY@2026-07 | 1.97 | 1.97 | 一致 | from_to narrative |
| 314 | JP CPI yoy 2026-10 | series_store JP_CPI_YOY@2026-10 | 2.44 | 2.44 | 一致 | from_to narrative |
| 315 | Tokyo CPI yoy 2026-07 | series_store JP_CPI_TOKYO_YOY@2026-07 | 1.85 | 1.85 | 一致 | from_to narrative |
| 316 | Tokyo CPI yoy 2026-10 | series_store JP_CPI_TOKYO_YOY@2026-10 | 2.73 | 2.73 | 一致 | from_to narrative |
| 317 | JP policy rate 2025-10 | series_store JP_POLICY_RATE@2025-10 | 0.477 | 0.477 | 一致 | from_to narrative |
| 318 | JP policy rate 2026-07 | series_store JP_POLICY_RATE@2026-07 | 0.978 | 0.978 | 一致 | from_to narrative |
| 319 | JP policy rate 2026-10 | series_store JP_POLICY_RATE@2026-10 | 1.227 | 1.227 | 一致 | from_to narrative |
| 320 | CN PPI yoy 2025-10 | series_store CN_PPI_YOY@2025-10 | -2.1 | -2.1 | 一致 | from_to narrative |
| 321 | CN PPI yoy 2026-07 | series_store CN_PPI_YOY@2026-07 | 3.5 | 3.5 | 一致 | from_to narrative |
| 322 | CN PPI yoy 2026-10 | series_store CN_PPI_YOY@2026-10 | 5.7 | 5.7 | 一致 | from_to narrative |
| 323 | CN CPI yoy 2025-10 | series_store CN_CPI_YOY@2025-10 | 0.2 | 0.2 | 一致 | from_to narrative |
| 324 | CN CPI yoy 2026-07 | series_store CN_CPI_YOY@2026-07 | 0.5 | 0.5 | 一致 | from_to narrative |
| 325 | CN CPI yoy 2026-10 | series_store CN_CPI_YOY@2026-10 | 0.7 | 0.7 | 一致 | from_to narrative |
| 326 | CN PMI 2025-10 | series_store CN_PMI_MFG@2025-10 | 49.0 | 49.0 | 一致 | from_to narrative |
| 327 | CN PMI 2026-07 | series_store CN_PMI_MFG@2026-07 | 49.2 | 49.2 | 一致 | from_to narrative |
| 328 | CN PMI 2026-10 | series_store CN_PMI_MFG@2026-10 | 49.3 | 49.3 | 一致 | from_to narrative |
| 329 | CPI yoy 2026-02 | series_store CPI yoy(2026-02) | 2.434 | 2.434 | 一致 | turnings/TR1 link2 |
| 330 | CPI yoy 2026-04 | series_store CPI yoy(2026-04) | 3.7792 | 3.78 | 一致 | turnings/TR1 link2 |
| 331 | CPI yoy 2026-05 | series_store CPI yoy(2026-05) | 4.1666 | 4.1666 | 一致 | turnings/TR1 link2 |
| 332 | CPI yoy 2026-07 | series_store CPI yoy(2026-07) | 3.3039 | 3.30 | 一致 | turnings/TR1 link2 |
| 333 | CPI yoy 2026-08 | series_store CPI yoy(2026-08) | 3.353 | 3.35 | 一致 | turnings/TR1 link2 |
| 334 | CPI yoy 2026-09 | series_store CPI yoy(2026-09) | 3.7173 | 3.72 | 一致 | turnings/TR1 link2 |
| 335 | CPI yoy 2026-10 absent (base 2025-10 missing) | series_store CPI 2025-10 | 不可得(null) | absent | 一致 |  |
| 336 | CPI yoy peak 2026-05 rounded 4.17 | series_store CPI yoy(2026-05) | 4.17 | 4.17 | 一致 |  |
| 337 | CPI yoy peak month (valid yoy) | series_store CPI yoy argmax 2025-11..2026-09 | 2026-05 | 2026-05 | 一致 | 2026-05 见顶 |
| 338 | CPI yoy low month | series_store CPI yoy argmin 2025-11..2026-10 | 2026-01 | 2026-01 | 一致 | 低点均在 2026-01 |
| 339 | CPI yoy after peak never exceeds peak | series_store CPI yoy max 2026-06..2026-09 = 3.7173 (peak 2026-05) | True | True | 一致 | 未再越过高点 |
| 340 | CORE_CPI yoy 2026-02 | series_store CORE_CPI yoy(2026-02) | 2.4725 | 2.47 | 一致 | TR1 link1 / candidate face / latest valid yoy |
| 341 | CORE_CPI yoy 2026-05 | series_store CORE_CPI yoy(2026-05) | 2.8229 | 2.8229 | 一致 | TR1 link1 / candidate face / latest valid yoy |
| 342 | CORE_CPI yoy 2026-08 | series_store CORE_CPI yoy(2026-08) | 2.4462 | 2.4462 | 一致 | TR1 link1 / candidate face / latest valid yoy |
| 343 | CORE_CPI yoy 2026-09 | series_store CORE_CPI yoy(2026-09) | 2.5658 | 2.57 | 一致 | TR1 link1 / candidate face / latest valid yoy |
| 344 | CORE_CPI yoy 2026-05 rounded | series_store CORE_CPI yoy(2026-05) | 2.8229 | 2.82 | 一致 |  |
| 345 | CORE_PCE yoy 2026-05 | series_store CORE_PCE yoy(2026-05) | 3.1617 | 3.16 | 一致 |  |
| 346 | CORE_PCE yoy 2026-07 | series_store CORE_PCE yoy(2026-07) | 2.9953 | 3.00 | 一致 |  |
| 347 | CORE_PCE yoy 2026-09 | series_store CORE_PCE yoy(2026-09) | 3.1212 | 3.12 | 一致 |  |
| 348 | CORE_PCE yoy peak month | series_store CORE_PCE yoy argmax 2025-11..2026-09 | 2026-05 | 2026-05 | 一致 | 月度同比自2026-05高点3.16回落 |
| 349 | CORE_PCE yoy after peak never exceeds peak | series_store max 2026-06..2026-09 = 3.1212 (peak 2026-05) | True | True | 一致 | 未再越过高点 |
| 350 | CORE_PCE latest obs month = 2026-09 | series_store CORE_PCE dates | 2026-09 | 2026-09 | 一致 |  |
| 351 | CORE_PCE 2026-10 not visible at cutoff | series_store + seat rule | absent | >2026-11-23 | 一致 |  |
| 352 | INDPRO yoy 2025-11 | series_store INDPRO yoy(2025-11) | 1.7543 | 1.7543 | 一致 | turnings[1] |
| 353 | INDPRO yoy 2026-02 | series_store INDPRO yoy(2026-02) | 0.7972 | 0.7972 | 一致 | turnings[1] |
| 354 | INDPRO yoy halved (ratio < 0.5) | series_store INDPRO yoy ratio 2026-02/2025-11 | 0.4544 | <0.5 | 一致 | 折半 |
| 355 | EA_HICP_YOY 2026-01 | series_store EA_HICP_YOY@2026-01 | 1.7 | 1.7 | 一致 |  |
| 356 | EA_HICP_YOY 2026-02 | series_store EA_HICP_YOY@2026-02 | 1.9 | 1.9 | 一致 |  |
| 357 | EA_HICP_YOY 2026-05 | series_store EA_HICP_YOY@2026-05 | 3.2 | 3.2 | 一致 |  |
| 358 | EA_HICP_YOY 2026-06 | series_store EA_HICP_YOY@2026-06 | 2.8 | 2.8 | 一致 |  |
| 359 | EA HICP low month | series_store EA_HICP_YOY argmin 2025-11..2026-10 | 2026-01 | 2026-01 | 一致 | 自2026-01低点1.7 |
| 360 | EA HICP high month (本轮最高) | series_store EA_HICP_YOY argmax 2025-11..2026-10 | 2026-10 | 2026-10 | 一致 | 升至本轮最高 |
| 361 | EA HICP 连续上行 2026-01..2026-05 | series_store EA_HICP_YOY monotonic up | True | True | 一致 |  |
| 362 | EA HICP 2026-03起加速 (inc03>inc02) | series_store EA_HICP_YOY increments | 0.70 vs 0.20 | inc03>inc02 | 一致 |  |
| 363 | EA HICP 再度上行 2026-07..2026-10 | series_store EA_HICP_YOY monotonic up | True | True | 一致 | 自2026-07再度上行 |
| 364 | EA HICP 2026-08至10加速 (each increment > 2026-07 increment) | series_store EA_HICP_YOY increments 07..10 | 0.10 0.30 0.60 0.20 | d08,d09,d10 > d07 | 一致 | note: 2026-10 increment smaller than 2026-09 |
| 365 | EA HICP latest visible obs at cutoff = 2026-10 | series_store + seat rule | ["2026-10-01", "2026-10-31"] | 2026-10 | 一致 |  |
| 366 | CN_PPI_YOY 2026-02 | series_store CN_PPI_YOY@2026-02 | -0.9 | -0.9 | 一致 | TR1 link1 / turning[0] |
| 367 | CN_PPI_YOY 2026-05 | series_store CN_PPI_YOY@2026-05 | 3.9 | 3.9 | 一致 | TR1 link1 / turning[0] |
| 368 | CN PPI low month (window) | series_store CN_PPI_YOY argmin 2025-11..2026-10 | 2025-11 | 2025-11 | 一致 | 中国 PPI 低点在 2025-11 |
| 369 | CN PPI 连升 2025-11..2026-05 | series_store CN_PPI_YOY monotonic up | True | True | 一致 | 此后连升 (to resonance-window end) |
| 370 | CN PPI latest = window high | series_store CN_PPI_YOY argmax 2025-11..2026-10 | 2026-10 | 2026-10 | 一致 | 续创本轮新高 |
| 371 | CN PPI rising every month 2026-07..2026-10 | series_store CN_PPI_YOY | [3.5, 3.8, 5.0, 5.7] | strictly increasing | 一致 | 续创本轮新高 / 2026-07回落至3.5后升至5.7 |
| 372 | CN PPI largest 12m swing among four regions | series_store 12m change: CN PPI vs CPI/EA/JP/CN CPI | 7.80 vs max 1.90 | largest | 一致 | 四地最大价格摆动 |
| 373 | CN_CPI_YOY 2026-01 | series_store CN_CPI_YOY@2026-01 | 0.2 | 0.2 | 一致 | candidate face |
| 374 | CN_CPI_YOY 2026-04 | series_store CN_CPI_YOY@2026-04 | 1.2 | 1.2 | 一致 | candidate face |
| 375 | CN PMI months above 50 | series_store CN_PMI_MFG 2025-11..2026-10 | 2025-12=50.1 2026-03=50.4 2026-04=50.3 2026-06=50.3 2026-09=50.1 | 2025-12=50.1 2026-03=50.4 2026-04=50.3 2026-06=50.3 2026-09=50.1 | 一致 |  |
| 376 | CN PMI 2026-05 = 50.0 | series_store CN_PMI_MFG@2026-05 | 50.0 | 50.0 | 一致 |  |
| 377 | CN PMI other months within 49.0..49.8 | series_store CN_PMI_MFG min/max of others | 49.0..49.8 | 49.0..49.8 | 一致 | n=6 |
| 378 | CN PMI yoy percent 2025-10 | series_store CN_PMI_MFG 2025-10 vs 2024-10 (pct change) | -2.1956 | -2.2 | 一致 | 同比口径 -2.2→-0.2→+0.61; pp difference = -1.10 |
| 379 | CN PMI yoy percent 2026-07 | series_store CN_PMI_MFG 2026-07 vs 2025-07 (pct change) | -0.2028 | -0.2 | 一致 | 同比口径 -2.2→-0.2→+0.61; pp difference = -0.10 |
| 380 | CN PMI yoy percent 2026-10 | series_store CN_PMI_MFG 2026-10 vs 2025-10 (pct change) | 0.6122 | 0.61 | 一致 | 同比口径 -2.2→-0.2→+0.61; pp difference = 0.30 |
| 381 | JP_CPI_YOY 2025-11 | series_store JP_CPI_YOY@2025-11 | 2.9 | 2.9 | 一致 | turnings[2] |
| 382 | JP_CPI_YOY 2025-12 | series_store JP_CPI_YOY@2025-12 | 2.13 | 2.13 | 一致 | turnings[2] |
| 383 | JP_CPI_YOY 2026-01 | series_store JP_CPI_YOY@2026-01 | 1.51 | 1.51 | 一致 | turnings[2] |
| 384 | JP_CPI_YOY 2026-02 | series_store JP_CPI_YOY@2026-02 | 1.27 | 1.27 | 一致 | turnings[2] |
| 385 | JP_CPI_YOY 2026-03 | series_store JP_CPI_YOY@2026-03 | 1.46 | 1.46 | 一致 | turnings[2] |
| 386 | JP_CPI_YOY 2026-04 | series_store JP_CPI_YOY@2026-04 | 1.38 | 1.38 | 一致 | turnings[2] |
| 387 | JP_CPI_YOY 2025-01 | series_store JP_CPI_YOY@2025-01 | 4.03 | 4.03 | 一致 | 自 2025-01 高点 4.03 |
| 388 | JP CPI low = 2026-02 since 2025-01 | series_store JP_CPI_YOY argmin 2025-01..2026-02 | 2026-02 | 2026-02 | 一致 |  |
| 389 | JP CPI rebound 2025-09 | series_store JP_CPI_YOY 2025-09 vs 2025-08 | 2.91 vs 2.72 | up | 一致 | 其间 2025-09、2025-10 小幅回升 |
| 390 | JP CPI rebound 2025-10 | series_store JP_CPI_YOY 2025-10 vs 2025-09 | 2.99 vs 2.91 | up | 一致 |  |
| 391 | JP CPI 持续回升自 2026-05 起 (monotonic up to 2026-10) | series_store JP_CPI_YOY monotonic up | True | True | 一致 |  |
| 392 | JP CPI first uptick month after trough = 2026-03 | series_store JP_CPI_YOY 2026-03 vs 2026-02 | 1.46 vs 1.27 | up | 一致 | 全国口径的回升起点(2026-03) |
| 393 | JP_CPI_TOKYO_YOY 2026-06 | series_store JP_CPI_TOKYO_YOY@2026-06 | 1.6 | 1.6 | 一致 | turning supplement |
| 394 | JP_CPI_TOKYO_YOY 2026-08 | series_store JP_CPI_TOKYO_YOY@2026-08 | 1.9 | 1.9 | 一致 | turning supplement |
| 395 | JP_CPI_TOKYO_YOY 2026-09 | series_store JP_CPI_TOKYO_YOY@2026-09 | 2.69 | 2.69 | 一致 | turning supplement |
| 396 | Tokyo CPI rising every month 2026-06..2026-10 | series_store JP_CPI_TOKYO_YOY | [1.6, 1.85, 1.9, 2.69, 2.73] | strictly increasing | 一致 | 东京口径的上行起点(2026-06) |
| 397 | JP_POLICY_RATE 2025-11 | series_store JP_POLICY_RATE@2025-11 | 0.478 | 0.478 | 一致 |  |
| 398 | JP_POLICY_RATE 2025-12 | series_store JP_POLICY_RATE@2025-12 | 0.557 | 0.557 | 一致 |  |
| 399 | JP policy net change from 2025-11 (bp) | series_store (2026-10 - 2025-11)*100 | 74.9 | 75 | 一致 | 净 +75 个基点 |
| 400 | JP policy net change from 2025-12 (bp) | series_store (2026-10 - 2025-12)*100 | 67.0 | 67 | 一致 | 自 2025-12 起 +67bp |
| 401 | JP policy step 2025-12 (bp) | series_store (2025-12 - 2025-11)*100 | 7.9 | 8 | 一致 |  |
| 402 | JP policy step 2026-01 (bp) | series_store (2026-01 - 2025-12)*100 | 17.1 | 17 | 一致 |  |
| 403 | JP policy step 2026-06 (bp) | series_store (2026-06 - 2026-05)*100 | 11.4 | 11 | 一致 |  |
| 404 | JP policy step 2026-07 (bp) | series_store (2026-07 - 2026-06)*100 | 13.7 | 14 | 一致 |  |
| 405 | JP policy step 2026-09 (bp) | series_store (2026-09 - 2026-08)*100 | 6.6 | 7 | 一致 |  |
| 406 | JP policy step 2026-10 (bp) | series_store (2026-10 - 2026-09)*100 | 18.4 | 18 | 一致 |  |
| 407 | JP policy small rounding changes only in 2026-04 and 2026-08 | series_store JP_POLICY_RATE month steps | 2026-04:-0.10bp 2026-08:-0.10bp | 2026-04 and 2026-08 | 一致 | 各约零点一个基点的舍入变动 |
| 408 | JP policy no decline >= 0.5bp in window | series_store JP_POLICY_RATE month steps | ∅(空串) | none | 一致 | 窗内未回撤 |
| 409 | JP policy first in-window hike >= 1bp | series_store JP_POLICY_RATE steps 2025-11..2026-10 | 2025-12 | 2025-12 | 一致 | 日本月均利率上行自2025-12已开始 (window start 2025-11-23) |
| 410 | CPI yoy latest visible before 2026-06-11 = 2026-04 | series_store CPI latest visible (seat rule) = 2026-04-01 pub 2026-05-13 | 3.7792 | 3.78 | 一致 | obs month 2026-04 |
| 411 | CPI obs month visible before 2026-06-11 | series_store + seat rule | 2026-04 | 2026-04 | 一致 |  |
| 412 | CPI yoy latest visible before 2026-09-10 = 2026-07 | series_store CPI latest visible (seat rule) = 2026-07-01 pub 2026-08-13 | 3.3039 | 3.30 | 一致 | obs month 2026-07 |
| 413 | CPI obs month visible before 2026-09-10 | series_store + seat rule | 2026-07 | 2026-07 | 一致 |  |
| 414 | CPI yoy latest visible before 2026-09-16 = 2026-08 | series_store CPI latest visible (seat rule) = 2026-08-01 pub 2026-09-13 | 3.353 | 3.35 | 一致 | obs month 2026-08 |
| 415 | CPI obs month visible before 2026-09-16 | series_store + seat rule | 2026-08 | 2026-08 | 一致 |  |
| 416 | CPI yoy latest visible before 2026-09-18 = 2026-08 | series_store CPI latest visible (seat rule) = 2026-08-01 pub 2026-09-13 | 3.353 | 3.35 | 一致 | obs month 2026-08 |
| 417 | CPI obs month visible before 2026-09-18 | series_store + seat rule | 2026-08 | 2026-08 | 一致 |  |
| 418 | CPI 2026-09 obs published after 2026-09-18 | series_store + seat rule | 2026-10-13 | >2026-09-18 | 一致 | 决议后发布的 2026-09 观测 |
| 419 | CPI 2025-11 base present for 2026-11 yoy | series_store CPI@2025-11 | 325.063 | present | 一致 | 2026-11 起同比不受缺基期影响 |
| 420 | CPI yoy at cutoff not below 2.5 / 3.5 (SCN thresholds compatible) | series_store CPI yoy 2026-09 | 3.7172508442689933 | >=3.5 | 一致 |  |
| 421 | CORE_PCE yoy at cutoff not below 2.8 | series_store CORE_PCE yoy 2026-09 | 3.1211596029620203 | >=2.8 | 一致 |  |
| 422 | CN_NEW_LOANS latest obs month | series_store CN_NEW_LOANS | 2026-10 | 2026-10 | 一致 | C3 |
| 423 | candidate[0] CN_PPI_YOY value_before (2026-02) | series_store CN_PPI_YOY 同比%(水平序列)或观测值 | -0.9 | -0.9 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=-0.9 |
| 424 | candidate[0] CN_PPI_YOY value_after (2026-05) | series_store CN_PPI_YOY 同比%(水平序列)或观测值 | 3.9 | 3.9 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=3.9 |
| 425 | candidate[0] CN_PPI_YOY delta | series_store CN_PPI_YOY 同比%(水平序列)或观测值 后值−前值 | 4.8 | 4.8 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=4.8 |
| 426 | candidate[0] CN_PPI_YOY window = seat max \|3-apart change\| | series_store CN_PPI_YOY 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-02..2026-05 | 2026-02..2026-05 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 427 | candidate[1] CN_PMI_MFG value_before (2026-02) | series_store CN_PMI_MFG 同比%(水平序列)或观测值 | -2.3904 | -2.3904 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=-2.3904 |
| 428 | candidate[1] CN_PMI_MFG value_after (2026-05) | series_store CN_PMI_MFG 同比%(水平序列)或观测值 | 1.0101 | 1.0101 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=1.0101 |
| 429 | candidate[1] CN_PMI_MFG delta | series_store CN_PMI_MFG 同比%(水平序列)或观测值 后值−前值 | 3.4005 | 3.4005 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=3.4005 |
| 430 | candidate[1] CN_PMI_MFG window = seat max \|3-apart change\| | series_store CN_PMI_MFG 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-02..2026-05 | 2026-02..2026-05 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 431 | candidate[2] CPI value_before (2026-02) | series_store CPI 同比%(水平序列)或观测值 | 2.434 | 2.434 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=2.434 |
| 432 | candidate[2] CPI value_after (2026-05) | series_store CPI 同比%(水平序列)或观测值 | 4.1666 | 4.1666 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=4.1666 |
| 433 | candidate[2] CPI delta | series_store CPI 同比%(水平序列)或观测值 后值−前值 | 1.7326 | 1.7326 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=1.7326 |
| 434 | candidate[2] CPI window = seat max \|3-apart change\| | series_store CPI 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-02..2026-05 | 2026-02..2026-05 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 435 | candidate[3] JP_CPI_YOY value_before (2025-11) | series_store JP_CPI_YOY 同比%(水平序列)或观测值 | 2.9 | 2.9 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=2.9 |
| 436 | candidate[3] JP_CPI_YOY value_after (2026-02) | series_store JP_CPI_YOY 同比%(水平序列)或观测值 | 1.27 | 1.27 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=1.27 |
| 437 | candidate[3] JP_CPI_YOY delta | series_store JP_CPI_YOY 同比%(水平序列)或观测值 后值−前值 | -1.63 | -1.63 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=-1.63 |
| 438 | candidate[3] JP_CPI_YOY window = seat max \|3-apart change\| | series_store JP_CPI_YOY 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2025-11..2026-02 | 2025-11..2026-02 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 439 | candidate[4] EA_HICP_YOY value_before (2026-02) | series_store EA_HICP_YOY 同比%(水平序列)或观测值 | 1.9 | 1.9 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=1.9 |
| 440 | candidate[4] EA_HICP_YOY value_after (2026-05) | series_store EA_HICP_YOY 同比%(水平序列)或观测值 | 3.2 | 3.2 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=3.2 |
| 441 | candidate[4] EA_HICP_YOY delta | series_store EA_HICP_YOY 同比%(水平序列)或观测值 后值−前值 | 1.3 | 1.3 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=1.3 |
| 442 | candidate[4] EA_HICP_YOY window = seat max \|3-apart change\| | series_store EA_HICP_YOY 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-02..2026-05 | 2026-02..2026-05 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 443 | candidate[5] JP_CPI_TOKYO_YOY value_before (2026-06) | series_store JP_CPI_TOKYO_YOY 同比%(水平序列)或观测值 | 1.6 | 1.6 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=1.6 |
| 444 | candidate[5] JP_CPI_TOKYO_YOY value_after (2026-09) | series_store JP_CPI_TOKYO_YOY 同比%(水平序列)或观测值 | 2.69 | 2.69 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=2.69 |
| 445 | candidate[5] JP_CPI_TOKYO_YOY delta | series_store JP_CPI_TOKYO_YOY 同比%(水平序列)或观测值 后值−前值 | 1.09 | 1.09 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=1.09 |
| 446 | candidate[5] JP_CPI_TOKYO_YOY window = seat max \|3-apart change\| | series_store JP_CPI_TOKYO_YOY 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-06..2026-09 | 2026-06..2026-09 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 447 | candidate[6] CN_CPI_YOY value_before (2026-01) | series_store CN_CPI_YOY 同比%(水平序列)或观测值 | 0.2 | 0.2 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=0.2 |
| 448 | candidate[6] CN_CPI_YOY value_after (2026-04) | series_store CN_CPI_YOY 同比%(水平序列)或观测值 | 1.2 | 1.2 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=1.2 |
| 449 | candidate[6] CN_CPI_YOY delta | series_store CN_CPI_YOY 同比%(水平序列)或观测值 后值−前值 | 1.0 | 1.0 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=1.0 |
| 450 | candidate[6] CN_CPI_YOY window = seat max \|3-apart change\| | series_store CN_CPI_YOY 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-01..2026-04 | 2026-01..2026-04 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 451 | candidate[7] INDPRO value_before (2025-11) | series_store INDPRO 同比%(水平序列)或观测值 | 1.7543 | 1.7543 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=1.7543 |
| 452 | candidate[7] INDPRO value_after (2026-02) | series_store INDPRO 同比%(水平序列)或观测值 | 0.7972 | 0.7972 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=0.7972 |
| 453 | candidate[7] INDPRO delta | series_store INDPRO 同比%(水平序列)或观测值 后值−前值 | -0.9571 | -0.9571 | 一致 | 报告值=读者报告候选表 Δ;引擎面 delta=-0.9571 |
| 454 | candidate[7] INDPRO window = seat max \|3-apart change\| | series_store INDPRO 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2025-11..2026-02 | 2025-11..2026-02 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 455 | candidate[8] CORE_CPI value_before (2026-05) | series_store CORE_CPI 同比%(水平序列)或观测值 | 2.8229 | 2.8229 | 一致 | 报告值=读者报告候选表前值;引擎面 value_before=2.8229 |
| 456 | candidate[8] CORE_CPI value_after (2026-08) | series_store CORE_CPI 同比%(水平序列)或观测值 | 2.4462 | 2.4462 | 一致 | 报告值=读者报告候选表后值;引擎面 value_after=2.4462 |
| 457 | candidate[8] CORE_CPI delta | series_store CORE_CPI 同比%(水平序列)或观测值 后值−前值 | -0.3768 | -0.3767 | 偏离 | 报告值=读者报告候选表 Δ;引擎面 delta=-0.3767 |
| 458 | candidate[8] CORE_CPI window = seat max \|3-apart change\| | series_store CORE_CPI 同比%(水平序列)或观测值 窗=2025-11..2026-11 相隔三个观测 | 2026-05..2026-08 | 2026-05..2026-08 | 一致 | 候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算) |
| 459 | candidate face sorted by \|delta\| descending (9 rows) | MAP_REPORT.md 引擎转折候选面行序 | True | True | 一致 |  |
| 460 | turnings[1] CN_PMI_MFG z口径 2026-02 (judgment quote) | series_store CN_PMI_MFG 指数水平同比% | -2.3904 | -2.3904 | 一致 | 判断档 turnings[1].first_mover 「z口径 -2.3904→1.0101」 |
| 461 | turnings[1] CN_PMI_MFG z口径 2026-05 (judgment quote) | series_store CN_PMI_MFG 指数水平同比% | 1.0101 | 1.0101 | 一致 | 判断档 turnings[1].first_mover 「z口径 -2.3904→1.0101」 |
| 462 | turnings[0] 'CPI = 候选面最大美欧值' (\|delta\| max among US+EA candidates) | MAP_REPORT.md 引擎转折候选面 US/EA 行 | True | True | 一致 | US/EA \|Δ\|=[1.7326, 1.3, 0.9571, 0.3767] |

#### 1.2.3 日频(计点 133 行: 一致 133、偏离 0;信息行 0)

| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|---|
| 463 | 12m trio common day 2025-11-19 has UST_10Y | series_store UST_10Y@2025-11-19 | 4.13 | present | 一致 |  |
| 464 | 12m trio common day 2026-11-19 has UST_10Y | series_store UST_10Y@2026-11-19 | 5.04 | present | 一致 |  |
| 465 | 12m trio common day 2025-11-19 has TIPS_10Y | series_store TIPS_10Y@2025-11-19 | 1.86 | present | 一致 |  |
| 466 | 12m trio common day 2026-11-19 has TIPS_10Y | series_store TIPS_10Y@2026-11-19 | 2.88 | present | 一致 |  |
| 467 | 12m trio common day 2025-11-19 has BEI_10Y | series_store BEI_10Y@2025-11-19 | 2.27 | present | 一致 |  |
| 468 | 12m trio common day 2026-11-19 has BEI_10Y | series_store BEI_10Y@2026-11-19 | 2.16 | present | 一致 |  |
| 469 | 12m UST_10Y change (bp) | series_store (UST_10Y 2025-11-19→2026-11-19)*100 | 91.0 | 91 | 一致 |  |
| 470 | 12m TIPS_10Y change (bp) | series_store (TIPS_10Y 2025-11-19→2026-11-19)*100 | 102.0 | 102 | 一致 |  |
| 471 | 12m BEI_10Y change (bp) | series_store (BEI_10Y 2025-11-19→2026-11-19)*100 | -11.0 | -11 | 一致 |  |
| 472 | 12m trio residual change (bp) | series_store identity residual change*100 | 0.0 | 0 | 一致 | 恒等残差0 |
| 473 | 1m common days trio common day 2026-10-20 has UST_10Y | series_store UST_10Y@2026-10-20 | 5.12 | present | 一致 |  |
| 474 | 1m common days trio common day 2026-11-19 has UST_10Y | series_store UST_10Y@2026-11-19 | 5.04 | present | 一致 |  |
| 475 | 1m common days trio common day 2026-10-20 has TIPS_10Y | series_store TIPS_10Y@2026-10-20 | 2.77 | present | 一致 |  |
| 476 | 1m common days trio common day 2026-11-19 has TIPS_10Y | series_store TIPS_10Y@2026-11-19 | 2.88 | present | 一致 |  |
| 477 | 1m common days trio common day 2026-10-20 has BEI_10Y | series_store BEI_10Y@2026-10-20 | 2.35 | present | 一致 |  |
| 478 | 1m common days trio common day 2026-11-19 has BEI_10Y | series_store BEI_10Y@2026-11-19 | 2.16 | present | 一致 |  |
| 479 | 1m common days UST_10Y change (bp) | series_store (UST_10Y 2026-10-20→2026-11-19)*100 | -8.0 | -8.0 | 一致 |  |
| 480 | 1m common days TIPS_10Y change (bp) | series_store (TIPS_10Y 2026-10-20→2026-11-19)*100 | 11.0 | 11.0 | 一致 |  |
| 481 | 1m common days BEI_10Y change (bp) | series_store (BEI_10Y 2026-10-20→2026-11-19)*100 | -19.0 | -19.0 | 一致 |  |
| 482 | 1m common days trio residual change (bp) | series_store identity residual change*100 | 0.0 | 0 | 一致 | 恒等残差0 |
| 483 | UST_10Y level 2026-11-19 | series_store UST_10Y@2026-11-19 | 5.04 | 5.04 | 一致 | M1 link3 |
| 484 | TIPS_10Y level 2026-11-19 | series_store TIPS_10Y@2026-11-19 | 2.88 | 2.88 | 一致 | M1 link3 |
| 485 | BEI_10Y level 2026-11-19 | series_store BEI_10Y@2026-11-19 | 2.16 | 2.16 | 一致 | M1 link3 |
| 486 | BEI_10Y level 2026-11-20 | series_store BEI_10Y@2026-11-20 | 2.15 | 2.15 | 一致 | latest |
| 487 | BEI_10Y 2026-02-27 | series_store BEI_10Y@2026-02-27 | 2.25 | 2.25 | 一致 | TR1 link2 |
| 488 | BEI_10Y 2026-05-04 | series_store BEI_10Y@2026-05-04 | 2.5 | 2.50 | 一致 | TR1 link2 |
| 489 | BEI_10Y 2026-06-10 | series_store BEI_10Y@2026-06-10 | 2.34 | 2.34 | 一致 | TR1 link2 |
| 490 | BEI_10Y 2026-10-23 | series_store BEI_10Y@2026-10-23 | 2.34 | 2.34 | 一致 | TR1 link2 |
| 491 | BEI_10Y range after 2026-06-17 | series_store BEI_10Y min..max | 2.15..2.40 | 2.15..2.40 | 一致 |  |
| 492 | BEI_10Y 2026-10-23→2026-11-20 calendar days | dates | 28 | 28 | 一致 |  |
| 493 | rates_decomposition.nominal_bp | series_store recompute | -8.0 | -8.0 | 一致 | judgment field |
| 494 | rates_decomposition.real_bp | series_store recompute | 11.0 | 11.0 | 一致 | judgment field |
| 495 | rates_decomposition.bei_bp | series_store recompute | -19.0 | -19.0 | 一致 | judgment field |
| 496 | rates_decomposition window | judgment field | 2026-10-20..2026-11-19 | 2026-10-20..2026-11-19 | 一致 |  |
| 497 | asset SPX 2026-10-23→2026-11-23 | series_store SPX 2026-10-23→2026-11-23 | -5.5069 | -5.51 | 一致 | asset_returns_echo |
| 498 | asset SHCOMP 2026-10-23→2026-11-23 | series_store SHCOMP 2026-10-23→2026-11-23 | -4.1059 | -4.11 | 一致 | asset_returns_echo |
| 499 | asset DAX 2026-10-23→2026-11-23 | series_store DAX 2026-10-23→2026-11-23 | 0.1104 | 0.11 | 一致 | asset_returns_echo |
| 500 | asset NIKKEI225 2026-10-23→2026-11-20 | series_store NIKKEI225 2026-10-23→2026-11-20 | -9.9796 | -9.98 | 一致 | asset_returns_echo |
| 501 | asset VIX 2026-10-23→2026-11-23 | series_store VIX 2026-10-23→2026-11-23 | 38.8689 | 38.87 | 一致 | asset_returns_echo |
| 502 | asset DXY 2026-10-23→2026-11-23 | series_store DXY 2026-10-23→2026-11-23 | 2.2287 | 2.23 | 一致 | asset_returns_echo |
| 503 | asset GOLD_F 2026-10-23→2026-11-23 | series_store GOLD_F 2026-10-23→2026-11-23 | -8.0516 | -8.05 | 一致 | asset_returns_echo |
| 504 | asset UST_10Y 2026-10-23→2026-11-19 | series_store UST_10Y 2026-10-23→2026-11-19 | 0.8 | 0.8 | 一致 | asset_returns_echo |
| 505 | close basis SPX 2026-10-23→2026-11-20 | series_store SPX 2026-10-23→2026-11-20 | -9.3562 | -9.36 | 一致 | TR1 link3 close basis |
| 506 | close basis DAX 2026-10-23→2026-11-20 | series_store DAX 2026-10-23→2026-11-20 | -1.5046 | -1.50 | 一致 | TR1 link3 close basis |
| 507 | close basis CAC40 2026-10-23→2026-11-20 | series_store CAC40 2026-10-23→2026-11-20 | 1.8622 | 1.86 | 一致 | TR1 link3 close basis |
| 508 | close basis NIKKEI225 2026-10-23→2026-11-20 | series_store NIKKEI225 2026-10-23→2026-11-20 | -9.9796 | -9.98 | 一致 | TR1 link3 close basis |
| 509 | close basis VIX 2026-10-23→2026-11-20 | series_store VIX 2026-10-23→2026-11-20 | 84.5244 | 84.52 | 一致 | TR1 link3 close basis |
| 510 | VIX 2026-10-23 | series_store VIX@2026-10-23 | 19.45 | 19.45 | 一致 |  |
| 511 | VIX 2026-11-23 | series_store VIX@2026-11-23 | 27.01 | 27.01 | 一致 |  |
| 512 | C1 level UST_10Y | series_store UST_10Y latest 2026-11-19 | 5.04 | 5.04 | 一致 | latest level at cutoff |
| 513 | C1 level TIPS_10Y | series_store TIPS_10Y latest 2026-11-19 | 2.88 | 2.88 | 一致 | latest level at cutoff |
| 514 | C1 level BEI_10Y | series_store BEI_10Y latest 2026-11-20 | 2.15 | 2.15 | 一致 | latest level at cutoff |
| 515 | C1 level VIX | series_store VIX latest 2026-11-23 | 27.01 | 27.01 | 一致 | latest level at cutoff |
| 516 | C1 level USDJPY | series_store USDJPY latest 2026-11-23 | 159.347 | 159.35 | 一致 | latest level at cutoff |
| 517 | C1 level DFF | series_store DFF latest 2026-11-19 | 3.88 | 3.88 | 一致 | latest level at cutoff |
| 518 | C1 level JP_POLICY_RATE | series_store JP_POLICY_RATE latest 2026-10-01 | 1.227 | 1.227 | 一致 | latest level at cutoff |
| 519 | C1 level CN_PPI_YOY | series_store CN_PPI_YOY latest 2026-10-01 | 5.7 | 5.7 | 一致 | latest level at cutoff |
| 520 | C1 level CN_CPI_YOY | series_store CN_CPI_YOY latest 2026-10-01 | 0.7 | 0.7 | 一致 | latest level at cutoff |
| 521 | C1 level CN_PMI_MFG | series_store CN_PMI_MFG latest 2026-10-01 | 49.3 | 49.3 | 一致 | latest level at cutoff |
| 522 | C1 level HY_OAS | series_store HY_OAS@2026-11-19 | 3.52 | 3.52 | 一致 |  |
| 523 | M1 link4 SPX near 1m | series_store SPX 2026-10-23→2026-11-23 | -5.5069 | -5.51 | 一致 | SPX/VIX 2026-10-23→2026-11-23 |
| 524 | M1 link4 NIKKEI225 near 1m | series_store NIKKEI225 2026-10-23→2026-11-20 | -9.9796 | -9.98 | 一致 | SPX/VIX 2026-10-23→2026-11-23 |
| 525 | M1 link4 GOLD_F near 1m | series_store GOLD_F 2026-10-23→2026-11-23 | -8.0516 | -8.05 | 一致 | SPX/VIX 2026-10-23→2026-11-23 |
| 526 | M1 link4 DXY near 1m | series_store DXY 2026-10-23→2026-11-23 | 2.2287 | 2.23 | 一致 | SPX/VIX 2026-10-23→2026-11-23 |
| 527 | HY_OAS series high date | series_store HY_OAS argmax | 2025-04-07 | 2025-04-07 | 一致 |  |
| 528 | HY_OAS series high | series_store HY_OAS@2025-04-07 | 4.61 | 4.61 | 一致 |  |
| 529 | HY_OAS first date (自 2023-11-21 起) | series_store HY_OAS first date | 2023-11-21 | 2023-11-21 | 一致 |  |
| 530 | HY_OAS percentile of current value | series_store HY_OAS share of history <= current *100 | 91.9847 | 92 | 一致 | 约第 92 百分位 |
| 531 | HY_OAS last earlier date with value >= current | series_store HY_OAS | 2025-05-09 | 2025-05-09 | 一致 | 为 2025-05-09 以来最高 |
| 532 | HY_OAS 1w change vs 2026-11-13 (pp) | series_store HY_OAS 2026-11-19 - 2026-11-13 | 0.29 | 0.29 | 一致 |  |
| 533 | HY_OAS strict 7d change (pp) | series_store HY_OAS 2026-11-19 - 2026-11-12 | 0.32 | 0.32 | 一致 |  |
| 534 | HY_OAS 12m change (pp) | series_store HY_OAS 2026-11-19 - 2025-11-19 | 0.35 | 0.35 | 一致 |  |
| 535 | BRENT_F month-end 2026-02 | series_store BRENT_F@2026-02-27 | 72.48 | 72.48 | 一致 | TR1 link1 |
| 536 | BRENT_F month-end 2026-03 | series_store BRENT_F@2026-03-31 | 118.35 | 118.35 | 一致 | TR1 link1 |
| 537 | BRENT_F month-end 2026-05 | series_store BRENT_F@2026-05-29 | 92.05 | 92.05 | 一致 | TR1 link1 |
| 538 | BRENT_F first-last 2026-02→2026-05 | series_store BRENT_F month-ends | 27.0006 | 27.00 | 一致 | 首尾 +27.00% |
| 539 | BRENT_F level 2026-11-23 | series_store BRENT_F@2026-11-23 | 88.19 | 88.19 | 一致 |  |
| 540 | BRENT_F MTD | series_store BRENT_F 2026-10-30→2026-11-23 | -25.034 | -25.03 | 一致 | 当月至今 |
| 541 | BRENT_F engine near-30-day | series_store BRENT_F 2026-10-23→2026-11-23 | -24.4431 | -24.44 | 一致 | engine face quoted |
| 542 | USDJPY 2026-11-23 | series_store USDJPY@2026-11-23 | 159.347 | 159.347 | 一致 |  |
| 543 | USDJPY 2026-10-23 | series_store USDJPY@2026-10-23 | 156.494 | 156.494 | 一致 |  |
| 544 | USDJPY near-30-day | series_store USDJPY 2026-10-23→2026-11-23 | 1.8231 | 1.82 | 一致 | TR2 |
| 545 | USDCNY@2026-11-23 present | series_store USDCNY | 6.6542 | present | 一致 | C3 ref |
| 546 | DFEDTARU@12m | series_store DFEDTARU latest 2025-11-23 | 4.0 | 4.0 | 一致 |  |
| 547 | DFEDTARU@3m | series_store DFEDTARU latest 2026-08-23 | 3.75 | 3.75 | 一致 |  |
| 548 | DFEDTARU@now | series_store DFEDTARU latest 2026-11-23 | 4.0 | 4.0 | 一致 |  |
| 549 | DFF@12m | series_store DFF latest 2025-11-22 | 3.88 | 3.88 | 一致 |  |
| 550 | DFF@3m | series_store DFF latest 2026-08-22 | 3.63 | 3.63 | 一致 |  |
| 551 | DFF@now | series_store DFF latest 2026-11-19 | 3.88 | 3.88 | 一致 |  |
| 552 | ECB_DFR@12m | series_store ECB_DFR latest 2025-06-11 | 2.0 | 2.0 | 一致 |  |
| 553 | ECB_DFR@3m | series_store ECB_DFR latest 2026-06-17 | 2.25 | 2.25 | 一致 |  |
| 554 | ECB_DFR@now | series_store ECB_DFR latest 2026-09-16 | 2.5 | 2.5 | 一致 |  |
| 555 | ECB_MRO@12m | series_store ECB_MRO latest 2025-06-11 | 2.15 | 2.15 | 一致 |  |
| 556 | ECB_MRO@3m | series_store ECB_MRO latest 2026-06-17 | 2.4 | 2.4 | 一致 |  |
| 557 | ECB_MRO@now | series_store ECB_MRO latest 2026-09-16 | 2.65 | 2.65 | 一致 |  |
| 558 | CN_LPR_1Y@12m | series_store CN_LPR_1Y latest 2025-11-20 | 3.0 | 3.0 | 一致 |  |
| 559 | CN_LPR_1Y@3m | series_store CN_LPR_1Y latest 2026-08-20 | 3.0 | 3.0 | 一致 |  |
| 560 | CN_LPR_1Y@now | series_store CN_LPR_1Y latest 2026-11-20 | 3.0 | 3.0 | 一致 |  |
| 561 | CN_OMO_7D@12m | series_store CN_OMO_7D latest 2025-11-14 | 1.4 | 1.4 | 一致 |  |
| 562 | CN_OMO_7D@3m | series_store CN_OMO_7D latest 2026-08-21 | 1.4 | 1.4 | 一致 |  |
| 563 | CN_OMO_7D@now | series_store CN_OMO_7D latest 2026-10-30 | 1.4 | 1.4 | 一致 |  |
| 564 | DFEDTARU anchor observation dates | series_store DFEDTARU latest<=anchor | 2025-11-23\|2026-08-23\|2026-11-23 | 2025-11-23\|2026-08-23\|2026-11-23 | 一致 |  |
| 565 | DFF anchor observation dates | series_store DFF latest<=anchor | 2025-11-22\|2026-08-22\|2026-11-19 | 2025-11-22\|2026-08-22\|2026-11-19 | 一致 |  |
| 566 | ECB_DFR anchor observation dates | series_store ECB_DFR latest<=anchor | 2025-06-11\|2026-06-17\|2026-09-16 | 2025-06-11\|2026-06-17\|2026-09-16 | 一致 |  |
| 567 | ECB_MRO anchor observation dates | series_store ECB_MRO latest<=anchor | 2025-06-11\|2026-06-17\|2026-09-16 | 2025-06-11\|2026-06-17\|2026-09-16 | 一致 |  |
| 568 | CN_LPR_1Y anchor observation dates | series_store CN_LPR_1Y latest<=anchor | 2025-11-20\|2026-08-20\|2026-11-20 | 2025-11-20\|2026-08-20\|2026-11-20 | 一致 |  |
| 569 | CN_OMO_7D anchor observation dates | series_store CN_OMO_7D latest<=anchor | 2025-11-14\|2026-08-21\|2026-10-30 | 2025-11-14\|2026-08-21\|2026-10-30 | 一致 |  |
| 570 | DFEDTARU changes in window | series_store DFEDTARU | 2025-12-11:4→3.75 2026-09-17:3.75→4 | 2025-12-11:4→3.75 2026-09-17:3.75→4 | 一致 | Fed effective dates |
| 571 | DFF changes >=20bp in window | series_store DFF | 2025-12-11:3.89→3.64 2026-09-17:3.63→3.88 | 2025-12-11:3.89→3.64 2026-09-17:3.63→3.88 | 一致 |  |
| 572 | ECB_DFR changes since 2025-06 | series_store ECB_DFR | 2026-06-17:2→2.25 2026-09-16:2.25→2.5 | 2026-06-17:2→2.25 2026-09-16:2.25→2.5 | 一致 |  |
| 573 | ECB_MRO changes since 2025-06 | series_store ECB_MRO | 2026-06-17:2.15→2.4 2026-09-16:2.4→2.65 | 2026-06-17:2.15→2.4 2026-09-16:2.4→2.65 | 一致 |  |
| 574 | ECB series end date | series_store ECB_MRO/ECB_DFR last date | 2026-09-16/2026-09-16 | 2026-09-16 | 一致 |  |
| 575 | ECB series lag days | 2026-11-23 - last obs | 68 | 68 | 一致 |  |
| 576 | CN_LPR_1Y no change in window | series_store CN_LPR_1Y | ∅(空串) | none | 一致 |  |
| 577 | CN_OMO_7D no change in window | series_store CN_OMO_7D | ∅(空串) | none | 一致 |  |
| 578 | CN_OMO_7D last observation lag (days) | 2026-11-23 - last obs | 24 | 24 | 一致 | 滞后24天 |
| 579 | last observation date SPX | series_store SPX last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 580 | last observation date DAX | series_store DAX last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 581 | last observation date CAC40 | series_store CAC40 last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 582 | last observation date VIX | series_store VIX last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 583 | last observation date GOLD_F | series_store GOLD_F last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 584 | last observation date DXY | series_store DXY last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 585 | last observation date BRENT_F | series_store BRENT_F last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 586 | last observation date USDJPY | series_store USDJPY last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 587 | last observation date SHCOMP | series_store SHCOMP last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 588 | last observation date NIKKEI225 | series_store NIKKEI225 last date | 2026-11-20 | 2026-11-20 | 一致 | basis note for cutoff-day observations |
| 589 | last observation date UST_10Y | series_store UST_10Y last date | 2026-11-19 | 2026-11-19 | 一致 | basis note for cutoff-day observations |
| 590 | last observation date TIPS_10Y | series_store TIPS_10Y last date | 2026-11-19 | 2026-11-19 | 一致 | basis note for cutoff-day observations |
| 591 | last observation date BEI_10Y | series_store BEI_10Y last date | 2026-11-20 | 2026-11-20 | 一致 | basis note for cutoff-day observations |
| 592 | last observation date HY_OAS | series_store HY_OAS last date | 2026-11-19 | 2026-11-19 | 一致 | basis note for cutoff-day observations |
| 593 | last observation date DFF | series_store DFF last date | 2026-11-19 | 2026-11-19 | 一致 | basis note for cutoff-day observations |
| 594 | last observation date DFEDTARU | series_store DFEDTARU last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |
| 595 | last observation date CN_POLICY_OVERNIGHT | series_store CN_POLICY_OVERNIGHT last date | 2026-11-23 | 2026-11-23 | 一致 | basis note for cutoff-day observations |

#### 1.2.4 历史段(计点 297 行: 一致 297、偏离 0;信息行 3)

| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|---|
| 596 | history periods count | judgment reader_map.history_periods | 3 | 3 (top-3) | 一致 |  |
| 597 | 2025-03 candidate month = engine rank 1 | report.json steps[61].data.top[0].candidate_month | 2025-03 | 2025-03 | 一致 |  |
| 598 | 2025-03 distance | report.json top[0].distance | 0.7272 | 0.7272 | 一致 | judgment period_label |
| 599 | 2025-03 distance percentile | report.json top[0].distance_percentile | 0.0 | 0.0 | 一致 | judgment period_label |
| 600 | 2025-03 valid candidates | report.json candidates.valid | 74 | 74 | 一致 |  |
| 601 | 2025-03 contribution 波动 (%) | report.json top[0].dims.volatility.contribution_share*100 | 42.1281 | 42.1 | 一致 |  |
| 602 | 2025-03 contribution 利率 (%) | report.json top[0].dims.rates.contribution_share*100 | 40.66 | 40.7 | 一致 |  |
| 603 | 2025-03 contribution 通胀 (%) | report.json top[0].dims.inflation.contribution_share*100 | 10.5401 | 10.5 | 一致 |  |
| 604 | 2025-03 contribution 估值 (%) | report.json top[0].dims.valuation.contribution_share*100 | 6.6684 | 6.7 | 一致 |  |
| 605 | 2025-03 contributions sum to 100 | judgment similarity text | 100.0 | 100.0 | 一致 | shares renormalised to accounted dims |
| 606 | 2025-03 gap magnitude CURVE_2S10S 12月变化 | report.json top[0].features_detail.CURVE_2S10S_d12m.gap (abs) | 1.5106 | 1.51 | 一致 |  |
| 607 | 2025-03 gap direction CURVE_2S10S 12月变化 | engine gap sign | - | - | 一致 |  |
| 608 | 2025-03 gap magnitude TIPS_10Y 12月变化 | report.json top[0].features_detail.TIPS_10Y_d12m.gap (abs) | 1.2987 | 1.30 | 一致 |  |
| 609 | 2025-03 gap direction TIPS_10Y 12月变化 | engine gap sign | + | + | 一致 |  |
| 610 | 2025-03 gap magnitude UST_10Y 12月变化 | report.json top[0].features_detail.UST_10Y_d12m.gap (abs) | 1.0681 | 1.07 | 一致 |  |
| 611 | 2025-03 gap direction UST_10Y 12月变化 | engine gap sign | + | + | 一致 |  |
| 612 | 2025-03 all \|gap\|>1 features listed | report.json top[0].features_detail | CURVE_2S10S_d12m TIPS_10Y_d12m UST_10Y_d12m | CURVE_2S10S_d12m TIPS_10Y_d12m UST_10Y_d12m | 一致 |  |
| 613 | 2025-03 missing feature HY_IG_gap_level disclosed | report.json top[0].missing_features | hist_17<36 | True | 一致 |  |
| 614 | 2025-03 missing feature HY_OAS_level disclosed | report.json top[0].missing_features | hist_17<36 | True | 一致 |  |
| 615 | 2025-03 match window = 12 months ending at candidate month | report.json feature_window_months x top[0].candidate_month | 2024-04..2025-03 | 2024-04..2025-03 | 一致 | cluster members 20: 2024-04..2025-11 |
| 616 | 2025-03 3m start month | judgment ex_post label | 2025-03 | 2025-03 | 一致 |  |
| 617 | 2025-03 3m end month | judgment ex_post label | 2025-06 | 2025-06 | 一致 |  |
| 618 | 2025-03 3m DFEDTARU (pp) | series_store DFEDTARU 2025-03-31→2025-06-30 | 0.0 | +0.00 | 一致 |  |
| 619 | 2025-03 3m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2025-03-01→2025-06-01 | -0.1 | -0.10 | 一致 |  |
| 620 | 2025-03 3m CPI (%) | series_store CPI 2025-03-01→2025-06-01 | 0.516 | +0.52 | 一致 |  |
| 621 | 2025-03 3m INDPRO (%) | series_store INDPRO 2025-03-01→2025-06-01 | 0.4336 | +0.43 | 一致 |  |
| 622 | 2025-03 3m SPX (%) | series_store SPX 2025-03-31→2025-06-30 | 10.5687 | +10.57 | 一致 |  |
| 623 | 2025-03 3m NIKKEI225 (%) | series_store NIKKEI225 2025-03-31→2025-06-30 | 13.6726 | +13.67 | 一致 |  |
| 624 | 2025-03 3m DAX (%) | series_store DAX 2025-03-31→2025-06-30 | 7.8784 | +7.88 | 一致 |  |
| 625 | 2025-03 3m SHCOMP (%) | series_store SHCOMP 2025-03-31→2025-06-30 | 3.258 | +3.26 | 一致 |  |
| 626 | 2025-03 3m GOLD_F (%) | series_store GOLD_F 2025-03-31→2025-06-30 | 5.921 | +5.92 | 一致 |  |
| 627 | 2025-03 3m DXY (%) | series_store DXY 2025-03-31→2025-06-30 | -7.0339 | -7.03 | 一致 |  |
| 628 | 2025-03 3m UST_10Y (pp) | series_store UST_10Y 2025-03-31→2025-06-30 | 0.01 | +0.01 | 一致 |  |
| 629 | 2025-03 6m start month | judgment ex_post label | 2025-03 | 2025-03 | 一致 |  |
| 630 | 2025-03 6m end month | judgment ex_post label | 2025-09 | 2025-09 | 一致 |  |
| 631 | 2025-03 6m DFEDTARU (pp) | series_store DFEDTARU 2025-03-31→2025-09-30 | -0.25 | -0.25 | 一致 |  |
| 632 | 2025-03 6m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2025-03-01→2025-09-01 | 0.2 | +0.20 | 一致 |  |
| 633 | 2025-03 6m CPI (%) | series_store CPI 2025-03-01→2025-09-01 | 1.3947 | +1.39 | 一致 |  |
| 634 | 2025-03 6m INDPRO (%) | series_store INDPRO 2025-03-01→2025-09-01 | 0.6211 | +0.62 | 一致 |  |
| 635 | 2025-03 6m SPX (%) | series_store SPX 2025-03-31→2025-09-30 | 19.1846 | +19.18 | 一致 |  |
| 636 | 2025-03 6m NIKKEI225 (%) | series_store NIKKEI225 2025-03-31→2025-09-30 | 26.153 | +26.15 | 一致 |  |
| 637 | 2025-03 6m DAX (%) | series_store DAX 2025-03-31→2025-09-30 | 7.748 | +7.75 | 一致 |  |
| 638 | 2025-03 6m SHCOMP (%) | series_store SHCOMP 2025-03-31→2025-09-30 | 16.3991 | +16.40 | 一致 |  |
| 639 | 2025-03 6m GOLD_F (%) | series_store GOLD_F 2025-03-31→2025-09-30 | 24.0297 | +24.03 | 一致 |  |
| 640 | 2025-03 6m DXY (%) | series_store DXY 2025-03-31→2025-09-30 | -6.1798 | -6.18 | 一致 |  |
| 641 | 2025-03 6m UST_10Y (pp) | series_store UST_10Y 2025-03-31→2025-09-30 | -0.07 | -0.07 | 一致 |  |
| 642 | 2025-03 12m start month | judgment ex_post label | 2025-03 | 2025-03 | 一致 |  |
| 643 | 2025-03 12m end month | judgment ex_post label | 2026-03 | 2026-03 | 一致 |  |
| 644 | 2025-03 12m DFEDTARU (pp) | series_store DFEDTARU 2025-03-31→2026-03-31 | -0.75 | -0.75 | 一致 |  |
| 645 | 2025-03 12m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2025-03-01→2026-03-01 | 0.1 | +0.10 | 一致 |  |
| 646 | 2025-03 12m CPI (%) | series_store CPI 2025-03-01→2026-03-01 | 3.286 | +3.29 | 一致 |  |
| 647 | 2025-03 12m INDPRO (%) | series_store INDPRO 2025-03-01→2026-03-01 | 0.6861 | +0.69 | 一致 |  |
| 648 | 2025-03 12m SPX (%) | series_store SPX 2025-03-31→2026-03-31 | 16.3345 | +16.33 | 一致 |  |
| 649 | 2025-03 12m NIKKEI225 (%) | series_store NIKKEI225 2025-03-31→2026-03-31 | 43.3667 | +43.37 | 一致 |  |
| 650 | 2025-03 12m DAX (%) | series_store DAX 2025-03-31→2026-03-31 | 2.3306 | +2.33 | 一致 |  |
| 651 | 2025-03 12m SHCOMP (%) | series_store SHCOMP 2025-03-31→2026-03-31 | 16.6714 | +16.67 | 一致 |  |
| 652 | 2025-03 12m GOLD_F (%) | series_store GOLD_F 2025-03-31→2026-03-31 | 48.828 | +48.83 | 一致 |  |
| 653 | 2025-03 12m DXY (%) | series_store DXY 2025-03-31→2026-03-31 | -4.0783 | -4.08 | 一致 |  |
| 654 | 2025-03 12m UST_10Y (pp) | series_store UST_10Y 2025-03-31→2026-03-31 | 0.07 | +0.07 | 一致 |  |
| 655 | 2025-03 engine aftermath SPX 1m | series_store SPX 2025-04-01→2025-04-30 | -1.136321 | -1.136321 | 一致 | engine face |
| 656 | 2025-03 engine aftermath SPX 3m | series_store SPX 2025-04-01→2025-06-30 | 10.152197 | 10.152197 | 一致 | engine face |
| 657 | 2025-03 engine aftermath SPX 6m | series_store SPX 2025-04-01→2025-09-30 | 18.735613 | 18.735613 | 一致 | engine face |
| 658 | 2025-03 engine aftermath SPX 12m | series_store SPX 2025-04-01→2026-03-31 | 15.896309 | 15.896309 | 一致 | engine face |
| 659 | 2025-03 engine aftermath UST_10Y 1m | series_store UST_10Y 2025-04-01→2025-04-30 | 0.0 | 0.0 | 一致 | engine face |
| 660 | 2025-03 engine aftermath UST_10Y 3m | series_store UST_10Y 2025-04-01→2025-06-30 | 0.07 | 0.07 | 一致 | engine face |
| 661 | 2025-03 engine aftermath UST_10Y 6m | series_store UST_10Y 2025-04-01→2025-09-30 | -0.01 | -0.01 | 一致 | engine face |
| 662 | 2025-03 engine aftermath UST_10Y 12m | series_store UST_10Y 2025-04-01→2026-03-31 | 0.13 | 0.13 | 一致 | engine face |
| 663 | 2025-03 engine aftermath DXY 1m | series_store DXY 2025-04-01→2025-04-30 | -4.594284 | -4.594284 | 一致 | engine face |
| 664 | 2025-03 engine aftermath DXY 3m | series_store DXY 2025-04-01→2025-06-30 | -7.078462 | -7.078462 | 一致 | engine face |
| 665 | 2025-03 engine aftermath DXY 6m | series_store DXY 2025-04-01→2025-09-30 | -6.224827 | -6.224827 | 一致 | engine face |
| 666 | 2025-03 engine aftermath DXY 12m | series_store DXY 2025-04-01→2026-03-31 | -4.124307 | -4.124307 | 一致 | engine face |
| 667 | 2025-03 engine aftermath GOLD_F 1m | series_store GOLD_F 2025-04-01→2025-04-30 | 5.502228 | 5.502228 | 一致 | engine face |
| 668 | 2025-03 engine aftermath GOLD_F 3m | series_store GOLD_F 2025-04-01→2025-06-30 | 5.139859 | 5.139859 | 一致 | engine face |
| 669 | 2025-03 engine aftermath GOLD_F 6m | series_store GOLD_F 2025-04-01→2025-09-30 | 23.115065 | 23.115065 | 一致 | engine face |
| 670 | 2025-03 engine aftermath GOLD_F 12m | series_store GOLD_F 2025-04-01→2026-03-31 | 47.730454 | 47.730454 | 一致 | engine face |
| 671 | 2025-03 known-at-time EA_HICP_YOY 2025-02 | series_store EA_HICP_YOY@2025-02 | 2.3 | 2.3 | 一致 |  |
| 672 | 2025-03 latest visible EA_HICP_YOY at 2025-03-31 | series_store + seat rule = 2025-02-01 (pub 2025-02-28) | 2025-02 | 2025-02 | 一致 |  |
| 673 | 2025-03 known-at-time JP_CPI_YOY 2025-02 | series_store JP_CPI_YOY@2025-02 | 3.66 | 3.66 | 一致 |  |
| 674 | 2025-03 latest visible JP_CPI_YOY at 2025-03-31 | series_store + seat rule = 2025-02-01 (pub 2025-03-20) | 2025-02 | 2025-02 | 一致 |  |
| 675 | 2025-03 known-at-time CN_PPI_YOY 2025-02 | series_store CN_PPI_YOY@2025-02 | -2.2 | -2.2 | 一致 |  |
| 676 | 2025-03 latest visible CN_PPI_YOY at 2025-03-31 | series_store + seat rule = 2025-02-01 (pub 2025-03-09) | 2025-02 | 2025-02 | 一致 |  |
| 677 | 2025-03 known-at-time CN_CPI_YOY 2025-02 | series_store CN_CPI_YOY@2025-02 | -0.7 | -0.7 | 一致 |  |
| 678 | 2025-03 latest visible CN_CPI_YOY at 2025-03-31 | series_store + seat rule = 2025-02-01 (pub 2025-03-09) | 2025-02 | 2025-02 | 一致 |  |
| 679 | 2025-03 sync labels present | judgment other_regions_sync | 中国分化、欧元区分化、日本同步 | —(仅席位直算) | 信息行(不计入) | informational: 标签三联在场(逐格比对见 sync 节 judgment 行) |
| 680 | 2025-03 coverage growth | report.json state_vector.growth.coverage | 0.1667 | 0.17 | 一致 |  |
| 681 | 2025-03 coverage inflation | report.json state_vector.inflation.coverage | 0.3333 | 0.33 | 一致 |  |
| 682 | 2025-03 coverage credit | report.json state_vector.credit.coverage | 0.5 | 0.5 | 一致 |  |
| 683 | 2022-06 candidate month = engine rank 2 | report.json steps[61].data.top[1].candidate_month | 2022-06 | 2022-06 | 一致 |  |
| 684 | 2022-06 distance | report.json top[1].distance | 0.7918 | 0.7918 | 一致 | judgment period_label |
| 685 | 2022-06 distance percentile | report.json top[1].distance_percentile | 1.3699 | 1.37 | 一致 | judgment period_label |
| 686 | 2022-06 contribution 利率 (%) | report.json top[1].dims.rates.contribution_share*100 | 51.9314 | 51.9 | 一致 |  |
| 687 | 2022-06 contribution 估值 (%) | report.json top[1].dims.valuation.contribution_share*100 | 33.6303 | 33.6 | 一致 |  |
| 688 | 2022-06 contribution 通胀 (%) | report.json top[1].dims.inflation.contribution_share*100 | 11.4111 | 11.4 | 一致 |  |
| 689 | 2022-06 contribution 波动 (%) | report.json top[1].dims.volatility.contribution_share*100 | 2.9815 | 3.0 | 一致 |  |
| 690 | 2022-06 contributions sum to 100 | judgment similarity text | 99.9 | 100.0 | 一致 | shares renormalised to accounted dims |
| 691 | 2022-06 gap magnitude TIPS_10Y 12月变化 | report.json top[1].features_detail.TIPS_10Y_d12m.gap (abs) | 1.7437 | 1.74 | 一致 |  |
| 692 | 2022-06 gap direction TIPS_10Y 12月变化 | engine gap sign | - | - | 一致 |  |
| 693 | 2022-06 gap magnitude CURVE_2S10S 12月变化 | report.json top[1].features_detail.CURVE_2S10S_d12m.gap (abs) | 1.4304 | 1.43 | 一致 |  |
| 694 | 2022-06 gap direction CURVE_2S10S 12月变化 | engine gap sign | + | + | 一致 |  |
| 695 | 2022-06 gap magnitude CURVE_2S10S水平 | report.json top[1].features_detail.CURVE_2S10S_level.gap (abs) | 1.2478 | 1.25 | 一致 |  |
| 696 | 2022-06 gap direction CURVE_2S10S水平 | engine gap sign | + | + | 一致 |  |
| 697 | 2022-06 gap magnitude SPX CAPE | report.json top[1].features_detail.SPX_CAPE_level.gap (abs) | 1.1707 | 1.17 | 一致 |  |
| 698 | 2022-06 gap direction SPX CAPE | engine gap sign | + | + | 一致 |  |
| 699 | 2022-06 all \|gap\|>1 features listed | report.json top[1].features_detail | CURVE_2S10S_d12m CURVE_2S10S_level SPX_CAPE_level TIPS_10Y_d12m | CURVE_2S10S_d12m CURVE_2S10S_level SPX_CAPE_level TIPS_10Y_d12m | 一致 |  |
| 700 | 2022-06 missing feature HY_IG_gap_level disclosed | report.json top[1].missing_features | no_value_at_candidate_month | True | 一致 |  |
| 701 | 2022-06 missing feature HY_OAS_level disclosed | report.json top[1].missing_features | no_value_at_candidate_month | True | 一致 |  |
| 702 | 2022-06 match window = 12 months ending at candidate month | report.json feature_window_months x top[1].candidate_month | 2021-07..2022-06 | 2021-07..2022-06 | 一致 | cluster members 23: 2021-07..2023-05 |
| 703 | 2022-06 3m start month | judgment ex_post label | 2022-06 | 2022-06 | 一致 |  |
| 704 | 2022-06 3m end month | judgment ex_post label | 2022-09 | 2022-09 | 一致 |  |
| 705 | 2022-06 3m DFEDTARU (pp) | series_store DFEDTARU 2022-06-30→2022-09-30 | 1.5 | +1.50 | 一致 |  |
| 706 | 2022-06 3m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2022-06-01→2022-09-01 | -0.1 | -0.10 | 一致 |  |
| 707 | 2022-06 3m CPI (%) | series_store CPI 2022-06-01→2022-09-01 | 0.4719 | +0.47 | 一致 |  |
| 708 | 2022-06 3m INDPRO (%) | series_store INDPRO 2022-06-01→2022-09-01 | 0.271 | +0.27 | 一致 |  |
| 709 | 2022-06 3m SPX (%) | series_store SPX 2022-06-30→2022-09-30 | -5.2771 | -5.28 | 一致 |  |
| 710 | 2022-06 3m NIKKEI225 (%) | series_store NIKKEI225 2022-06-30→2022-09-30 | -1.7271 | -1.73 | 一致 |  |
| 711 | 2022-06 3m DAX (%) | series_store DAX 2022-06-30→2022-09-30 | -5.2364 | -5.24 | 一致 |  |
| 712 | 2022-06 3m SHCOMP (%) | series_store SHCOMP 2022-06-30→2022-09-30 | -11.0111 | -11.01 | 一致 |  |
| 713 | 2022-06 3m GOLD_F (%) | series_store GOLD_F 2022-06-30→2022-09-30 | -7.4863 | -7.49 | 一致 |  |
| 714 | 2022-06 3m DXY (%) | series_store DXY 2022-06-30→2022-09-30 | 7.0971 | +7.10 | 一致 |  |
| 715 | 2022-06 3m UST_10Y (pp) | series_store UST_10Y 2022-06-30→2022-09-30 | 0.85 | +0.85 | 一致 |  |
| 716 | 2022-06 6m start month | judgment ex_post label | 2022-06 | 2022-06 | 一致 |  |
| 717 | 2022-06 6m end month | judgment ex_post label | 2022-12 | 2022-12 | 一致 |  |
| 718 | 2022-06 6m DFEDTARU (pp) | series_store DFEDTARU 2022-06-30→2022-12-31 | 2.75 | +2.75 | 一致 |  |
| 719 | 2022-06 6m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2022-06-01→2022-12-01 | -0.1 | -0.10 | 一致 |  |
| 720 | 2022-06 6m CPI (%) | series_store CPI 2022-06-01→2022-12-01 | 1.3138 | +1.31 | 一致 |  |
| 721 | 2022-06 6m INDPRO (%) | series_store INDPRO 2022-06-01→2022-12-01 | -1.239 | -1.24 | 一致 |  |
| 722 | 2022-06 6m SPX (%) | series_store SPX 2022-06-30→2022-12-30 | 1.4297 | +1.43 | 一致 |  |
| 723 | 2022-06 6m NIKKEI225 (%) | series_store NIKKEI225 2022-06-30→2022-12-30 | -1.1311 | -1.13 | 一致 |  |
| 724 | 2022-06 6m DAX (%) | series_store DAX 2022-06-30→2022-12-30 | 8.9162 | +8.92 | 一致 |  |
| 725 | 2022-06 6m SHCOMP (%) | series_store SHCOMP 2022-06-30→2022-12-30 | -9.1025 | -9.10 | 一致 |  |
| 726 | 2022-06 6m GOLD_F (%) | series_store GOLD_F 2022-06-30→2022-12-30 | 1.0458 | +1.05 | 一致 |  |
| 727 | 2022-06 6m DXY (%) | series_store DXY 2022-06-30→2022-12-30 | -1.1176 | -1.12 | 一致 |  |
| 728 | 2022-06 6m UST_10Y (pp) | series_store UST_10Y 2022-06-30→2022-12-30 | 0.9 | +0.90 | 一致 |  |
| 729 | 2022-06 12m start month | judgment ex_post label | 2022-06 | 2022-06 | 一致 |  |
| 730 | 2022-06 12m end month | judgment ex_post label | 2023-06 | 2023-06 | 一致 |  |
| 731 | 2022-06 12m DFEDTARU (pp) | series_store DFEDTARU 2022-06-30→2023-06-30 | 3.5 | +3.50 | 一致 |  |
| 732 | 2022-06 12m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2022-06-01→2023-06-01 | 0.0 | +0.00 | 一致 |  |
| 733 | 2022-06 12m CPI (%) | series_store CPI 2022-06-01→2023-06-01 | 3.0706 | +3.07 | 一致 |  |
| 734 | 2022-06 12m INDPRO (%) | series_store INDPRO 2022-06-01→2023-06-01 | -0.8893 | -0.89 | 一致 |  |
| 735 | 2022-06 12m SPX (%) | series_store SPX 2022-06-30→2023-06-30 | 17.5676 | +17.57 | 一致 |  |
| 736 | 2022-06 12m NIKKEI225 (%) | series_store NIKKEI225 2022-06-30→2023-06-30 | 25.7492 | +25.75 | 一致 |  |
| 737 | 2022-06 12m DAX (%) | series_store DAX 2022-06-30→2023-06-30 | 26.3156 | +26.32 | 一致 |  |
| 738 | 2022-06 12m SHCOMP (%) | series_store SHCOMP 2022-06-30→2023-06-30 | -5.7833 | -5.78 | 一致 |  |
| 739 | 2022-06 12m GOLD_F (%) | series_store GOLD_F 2022-06-30→2023-06-30 | 6.7559 | +6.76 | 一致 |  |
| 740 | 2022-06 12m DXY (%) | series_store DXY 2022-06-30→2023-06-30 | -1.7003 | -1.70 | 一致 |  |
| 741 | 2022-06 12m UST_10Y (pp) | series_store UST_10Y 2022-06-30→2023-06-30 | 0.83 | +0.83 | 一致 |  |
| 742 | 2022-06 engine aftermath SPX 1m | series_store SPX 2022-07-01→2022-07-29 | 7.972121 | 7.972121 | 一致 | engine face |
| 743 | 2022-06 engine aftermath SPX 3m | series_store SPX 2022-07-01→2022-09-30 | -6.266386 | -6.266386 | 一致 | engine face |
| 744 | 2022-06 engine aftermath SPX 6m | series_store SPX 2022-07-01→2022-12-30 | 0.370424 | 0.370424 | 一致 | engine face |
| 745 | 2022-06 engine aftermath SPX 12m | series_store SPX 2022-07-01→2023-06-30 | 16.339761 | 16.339761 | 一致 | engine face |
| 746 | 2022-06 engine aftermath UST_10Y 1m | series_store UST_10Y 2022-07-01→2022-07-29 | -0.21 | -0.21 | 一致 | engine face |
| 747 | 2022-06 engine aftermath UST_10Y 3m | series_store UST_10Y 2022-07-01→2022-09-30 | 0.95 | 0.95 | 一致 | engine face |
| 748 | 2022-06 engine aftermath UST_10Y 6m | series_store UST_10Y 2022-07-01→2022-12-30 | 1.0 | 1.0 | 一致 | engine face |
| 749 | 2022-06 engine aftermath UST_10Y 12m | series_store UST_10Y 2022-07-01→2023-06-30 | 0.93 | 0.93 | 一致 | engine face |
| 750 | 2022-06 engine aftermath DXY 1m | series_store DXY 2022-07-01→2022-07-29 | 0.722849 | 0.722849 | 一致 | engine face |
| 751 | 2022-06 engine aftermath DXY 3m | series_store DXY 2022-07-01→2022-09-30 | 6.638771 | 6.638771 | 一致 | engine face |
| 752 | 2022-06 engine aftermath DXY 6m | series_store DXY 2022-07-01→2022-12-30 | -1.540805 | -1.540805 | 一致 | engine face |
| 753 | 2022-06 engine aftermath DXY 12m | series_store DXY 2022-07-01→2023-06-30 | -2.120977 | -2.120977 | 一致 | engine face |
| 754 | 2022-06 engine aftermath GOLD_F 1m | series_store GOLD_F 2022-07-01→2022-07-29 | -2.142658 | -2.142658 | 一致 | engine face |
| 755 | 2022-06 engine aftermath GOLD_F 3m | series_store GOLD_F 2022-07-01→2022-09-30 | -7.188454 | -7.188454 | 一致 | engine face |
| 756 | 2022-06 engine aftermath GOLD_F 6m | series_store GOLD_F 2022-07-01→2022-12-30 | 1.371077 | 1.371077 | 一致 | engine face |
| 757 | 2022-06 engine aftermath GOLD_F 12m | series_store GOLD_F 2022-07-01→2023-06-30 | 7.099641 | 7.099641 | 一致 | engine face |
| 758 | 2022-06 known-at-time EA_HICP_YOY 2022-05 | series_store EA_HICP_YOY@2022-05 | 8.1 | 8.1 | 一致 |  |
| 759 | 2022-06 latest visible EA_HICP_YOY at 2022-06-30 | series_store + seat rule = 2022-05-01 (pub 2022-05-31) | 2022-05 | 2022-05 | 一致 |  |
| 760 | 2022-06 known-at-time JP_CPI_YOY 2022-05 | series_store JP_CPI_YOY@2022-05 | 2.46 | 2.46 | 一致 |  |
| 761 | 2022-06 latest visible JP_CPI_YOY at 2022-06-30 | series_store + seat rule = 2022-05-01 (pub 2022-06-20) | 2022-05 | 2022-05 | 一致 |  |
| 762 | 2022-06 known-at-time CN_PPI_YOY 2022-05 | series_store CN_PPI_YOY@2022-05 | 6.4 | 6.4 | 一致 |  |
| 763 | 2022-06 latest visible CN_PPI_YOY at 2022-06-30 | series_store + seat rule = 2022-05-01 (pub 2022-06-09) | 2022-05 | 2022-05 | 一致 |  |
| 764 | 2022-06 known-at-time CN_CPI_YOY 2022-05 | series_store CN_CPI_YOY@2022-05 | 2.1 | 2.1 | 一致 |  |
| 765 | 2022-06 latest visible CN_CPI_YOY at 2022-06-30 | series_store + seat rule = 2022-05-01 (pub 2022-06-09) | 2022-05 | 2022-05 | 一致 |  |
| 766 | 2022-06 sync labels present | judgment other_regions_sync | 中国同步、欧元区同步、日本同步 | —(仅席位直算) | 信息行(不计入) | informational: 标签三联在场(逐格比对见 sync 节 judgment 行) |
| 767 | 2022-06 coverage growth | report.json state_vector.growth.coverage | 0.1667 | 0.17 | 一致 |  |
| 768 | 2022-06 coverage inflation | report.json state_vector.inflation.coverage | 0.3333 | 0.33 | 一致 |  |
| 769 | 2022-06 coverage credit | report.json state_vector.credit.coverage | 0.5 | 0.5 | 一致 |  |
| 770 | 2023-10 candidate month = engine rank 3 | report.json steps[61].data.top[2].candidate_month | 2023-10 | 2023-10 | 一致 |  |
| 771 | 2023-10 distance | report.json top[2].distance | 1.0542 | 1.0542 | 一致 | judgment period_label |
| 772 | 2023-10 distance percentile | report.json top[2].distance_percentile | 30.137 | 30.14 | 一致 | judgment period_label |
| 773 | 2023-10 contribution 波动 (%) | report.json top[2].dims.volatility.contribution_share*100 | 60.1008 | 60.1 | 一致 |  |
| 774 | 2023-10 contribution 估值 (%) | report.json top[2].dims.valuation.contribution_share*100 | 21.199 | 21.2 | 一致 |  |
| 775 | 2023-10 contribution 利率 (%) | report.json top[2].dims.rates.contribution_share*100 | 10.9852 | 11.0 | 一致 |  |
| 776 | 2023-10 contribution 通胀 (%) | report.json top[2].dims.inflation.contribution_share*100 | 7.7093 | 7.7 | 一致 |  |
| 777 | 2023-10 contributions sum to 100 | judgment similarity text | 100.0 | 100.0 | 一致 | shares renormalised to accounted dims |
| 778 | 2023-10 gap magnitude SPX 21日已实现波动 | report.json top[2].features_detail.SPX_rv21.gap (abs) | 1.5664 | 1.57 | 一致 |  |
| 779 | 2023-10 gap direction SPX 21日已实现波动 | engine gap sign | + | + | 一致 |  |
| 780 | 2023-10 gap magnitude VIX水平 | report.json top[2].features_detail.VIX_level.gap (abs) | 1.3739 | 1.37 | 一致 |  |
| 781 | 2023-10 gap direction VIX水平 | engine gap sign | + | + | 一致 |  |
| 782 | 2023-10 gap magnitude SPX CAPE | report.json top[2].features_detail.SPX_CAPE_level.gap (abs) | 1.2374 | 1.24 | 一致 |  |
| 783 | 2023-10 gap direction SPX CAPE | engine gap sign | + | + | 一致 |  |
| 784 | 2023-10 gap magnitude CURVE_2S10S 12月变化 | report.json top[2].features_detail.CURVE_2S10S_d12m.gap (abs) | 1.0065 | 1.01 | 一致 |  |
| 785 | 2023-10 gap direction CURVE_2S10S 12月变化 | engine gap sign | - | - | 一致 |  |
| 786 | 2023-10 all \|gap\|>1 features listed | report.json top[2].features_detail | CURVE_2S10S_d12m SPX_CAPE_level SPX_rv21 VIX_level | CURVE_2S10S_d12m SPX_CAPE_level SPX_rv21 VIX_level | 一致 |  |
| 787 | 2023-10 missing feature HY_IG_gap_level disclosed | report.json top[2].missing_features | no_value_at_candidate_month | True | 一致 |  |
| 788 | 2023-10 missing feature HY_OAS_level disclosed | report.json top[2].missing_features | no_value_at_candidate_month | True | 一致 |  |
| 789 | 2023-10 match window = 12 months ending at candidate month | report.json feature_window_months x top[2].candidate_month | 2022-11..2023-10 | 2022-11..2023-10 | 一致 | cluster members 10: 2023-06..2024-03 |
| 790 | 2023-10 3m start month | judgment ex_post label | 2023-10 | 2023-10 | 一致 |  |
| 791 | 2023-10 3m end month | judgment ex_post label | 2024-01 | 2024-01 | 一致 |  |
| 792 | 2023-10 3m DFEDTARU (pp) | series_store DFEDTARU 2023-10-31→2024-01-31 | 0.0 | +0.00 | 一致 |  |
| 793 | 2023-10 3m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2023-10-01→2024-01-01 | -0.2 | -0.20 | 一致 |  |
| 794 | 2023-10 3m CPI (%) | series_store CPI 2023-10-01→2024-01-01 | 0.6506 | +0.65 | 一致 |  |
| 795 | 2023-10 3m INDPRO (%) | series_store INDPRO 2023-10-01→2024-01-01 | -1.2408 | -1.24 | 一致 |  |
| 796 | 2023-10 3m SPX (%) | series_store SPX 2023-10-31→2024-01-31 | 15.5432 | +15.54 | 一致 |  |
| 797 | 2023-10 3m NIKKEI225 (%) | series_store NIKKEI225 2023-10-31→2024-01-31 | 17.5893 | +17.59 | 一致 |  |
| 798 | 2023-10 3m DAX (%) | series_store DAX 2023-10-31→2024-01-31 | 14.1349 | +14.13 | 一致 |  |
| 799 | 2023-10 3m SHCOMP (%) | series_store SHCOMP 2023-10-31→2024-01-31 | -7.6264 | -7.63 | 一致 |  |
| 800 | 2023-10 3m GOLD_F (%) | series_store GOLD_F 2023-10-31→2024-01-31 | 2.7127 | +2.71 | 一致 |  |
| 801 | 2023-10 3m DXY (%) | series_store DXY 2023-10-31→2024-01-31 | -3.1783 | -3.18 | 一致 |  |
| 802 | 2023-10 3m UST_10Y (pp) | series_store UST_10Y 2023-10-31→2024-01-31 | -0.89 | -0.89 | 一致 |  |
| 803 | 2023-10 6m start month | judgment ex_post label | 2023-10 | 2023-10 | 一致 |  |
| 804 | 2023-10 6m end month | judgment ex_post label | 2024-04 | 2024-04 | 一致 |  |
| 805 | 2023-10 6m DFEDTARU (pp) | series_store DFEDTARU 2023-10-31→2024-04-30 | 0.0 | +0.00 | 一致 |  |
| 806 | 2023-10 6m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2023-10-01→2024-04-01 | 0.0 | +0.00 | 一致 |  |
| 807 | 2023-10 6m CPI (%) | series_store CPI 2023-10-01→2024-04-01 | 1.7313 | +1.73 | 一致 |  |
| 808 | 2023-10 6m INDPRO (%) | series_store INDPRO 2023-10-01→2024-04-01 | -0.2244 | -0.22 | 一致 |  |
| 809 | 2023-10 6m SPX (%) | series_store SPX 2023-10-31→2024-04-30 | 20.0746 | +20.07 | 一致 |  |
| 810 | 2023-10 6m NIKKEI225 (%) | series_store NIKKEI225 2023-10-31→2024-04-30 | 24.4559 | +24.46 | 一致 |  |
| 811 | 2023-10 6m DAX (%) | series_store DAX 2023-10-31→2024-04-30 | 21.0787 | +21.08 | 一致 |  |
| 812 | 2023-10 6m SHCOMP (%) | series_store SHCOMP 2023-10-31→2024-04-30 | 2.8506 | +2.85 | 一致 |  |
| 813 | 2023-10 6m GOLD_F (%) | series_store GOLD_F 2023-10-31→2024-04-30 | 15.4741 | +15.47 | 一致 |  |
| 814 | 2023-10 6m DXY (%) | series_store DXY 2023-10-31→2024-04-30 | -0.4125 | -0.41 | 一致 |  |
| 815 | 2023-10 6m UST_10Y (pp) | series_store UST_10Y 2023-10-31→2024-04-30 | -0.19 | -0.19 | 一致 |  |
| 816 | 2023-10 12m start month | judgment ex_post label | 2023-10 | 2023-10 | 一致 |  |
| 817 | 2023-10 12m end month | judgment ex_post label | 2024-10 | 2024-10 | 一致 |  |
| 818 | 2023-10 12m DFEDTARU (pp) | series_store DFEDTARU 2023-10-31→2024-10-31 | -0.5 | -0.50 | 一致 |  |
| 819 | 2023-10 12m UNEMPLOYMENT (pp) | series_store UNEMPLOYMENT 2023-10-01→2024-10-01 | 0.2 | +0.20 | 一致 |  |
| 820 | 2023-10 12m CPI (%) | series_store CPI 2023-10-01→2024-10-01 | 2.5788 | +2.58 | 一致 |  |
| 821 | 2023-10 12m INDPRO (%) | series_store INDPRO 2023-10-01→2024-10-01 | -0.9947 | -0.99 | 一致 |  |
| 822 | 2023-10 12m SPX (%) | series_store SPX 2023-10-31→2024-10-31 | 36.0449 | +36.04 | 一致 |  |
| 823 | 2023-10 12m NIKKEI225 (%) | series_store NIKKEI225 2023-10-31→2024-10-31 | 26.6452 | +26.65 | 一致 |  |
| 824 | 2023-10 12m DAX (%) | series_store DAX 2023-10-31→2024-10-31 | 28.8123 | +28.81 | 一致 |  |
| 825 | 2023-10 12m SHCOMP (%) | series_store SHCOMP 2023-10-31→2024-10-31 | 8.6477 | +8.65 | 一致 |  |
| 826 | 2023-10 12m GOLD_F (%) | series_store GOLD_F 2023-10-31→2024-10-31 | 37.8579 | +37.86 | 一致 |  |
| 827 | 2023-10 12m DXY (%) | series_store DXY 2023-10-31→2024-10-31 | -2.5127 | -2.51 | 一致 |  |
| 828 | 2023-10 12m UST_10Y (pp) | series_store UST_10Y 2023-10-31→2024-10-31 | -0.6 | -0.60 | 一致 |  |
| 829 | 2023-10 engine aftermath SPX 1m | series_store SPX 2023-11-01→2023-11-30 | 7.785532 | 7.785532 | 一致 | engine face |
| 830 | 2023-10 engine aftermath SPX 3m | series_store SPX 2023-11-01→2024-01-31 | 14.34191 | 14.34191 | 一致 | engine face |
| 831 | 2023-10 engine aftermath SPX 6m | series_store SPX 2023-11-01→2024-04-30 | 18.82625 | 18.82625 | 一致 | engine face |
| 832 | 2023-10 engine aftermath SPX 12m | series_store SPX 2023-11-01→2024-10-31 | 34.630459 | 34.630459 | 一致 | engine face |
| 833 | 2023-10 engine aftermath UST_10Y 1m | series_store UST_10Y 2023-11-01→2023-11-30 | -0.4 | -0.4 | 一致 | engine face |
| 834 | 2023-10 engine aftermath UST_10Y 3m | series_store UST_10Y 2023-11-01→2024-01-31 | -0.78 | -0.78 | 一致 | engine face |
| 835 | 2023-10 engine aftermath UST_10Y 6m | series_store UST_10Y 2023-11-01→2024-04-30 | -0.08 | -0.08 | 一致 | engine face |
| 836 | 2023-10 engine aftermath UST_10Y 12m | series_store UST_10Y 2023-11-01→2024-10-31 | -0.49 | -0.49 | 一致 | engine face |
| 837 | 2023-10 engine aftermath DXY 1m | series_store DXY 2023-11-01→2023-11-30 | -3.162422 | -3.162422 | 一致 | engine face |
| 838 | 2023-10 engine aftermath DXY 3m | series_store DXY 2023-11-01→2024-01-31 | -3.37762 | -3.37762 | 一致 | engine face |
| 839 | 2023-10 engine aftermath DXY 6m | series_store DXY 2023-11-01→2024-04-30 | -0.617511 | -0.617511 | 一致 | engine face |
| 840 | 2023-10 engine aftermath DXY 12m | series_store DXY 2023-11-01→2024-10-31 | -2.713318 | -2.713318 | 一致 | engine face |
| 841 | 2023-10 engine aftermath GOLD_F 1m | series_store GOLD_F 2023-11-01→2023-11-30 | 2.545911 | 2.545911 | 一致 | engine face |
| 842 | 2023-10 engine aftermath GOLD_F 3m | series_store GOLD_F 2023-11-01→2024-01-31 | 3.064146 | 3.064146 | 一致 | engine face |
| 843 | 2023-10 engine aftermath GOLD_F 6m | series_store GOLD_F 2023-11-01→2024-04-30 | 15.869177 | 15.869177 | 一致 | engine face |
| 844 | 2023-10 engine aftermath GOLD_F 12m | series_store GOLD_F 2023-11-01→2024-10-31 | 38.329562 | 38.329562 | 一致 | engine face |
| 845 | 2023-10 known-at-time EA_HICP_YOY 2023-10 | series_store EA_HICP_YOY@2023-10 | 2.9 | 2.9 | 一致 |  |
| 846 | 2023-10 latest visible EA_HICP_YOY at 2023-10-31 | series_store + seat rule = 2023-10-01 (pub 2023-10-31) | 2023-10 | 2023-10 | 一致 |  |
| 847 | 2023-10 known-at-time JP_CPI_YOY 2023-09 | series_store JP_CPI_YOY@2023-09 | 3.05 | 3.05 | 一致 |  |
| 848 | 2023-10 latest visible JP_CPI_YOY at 2023-10-31 | series_store + seat rule = 2023-09-01 (pub 2023-10-20) | 2023-09 | 2023-09 | 一致 |  |
| 849 | 2023-10 known-at-time CN_PPI_YOY 2023-09 | series_store CN_PPI_YOY@2023-09 | -2.5 | -2.5 | 一致 |  |
| 850 | 2023-10 latest visible CN_PPI_YOY at 2023-10-31 | series_store + seat rule = 2023-09-01 (pub 2023-10-09) | 2023-09 | 2023-09 | 一致 |  |
| 851 | 2023-10 known-at-time CN_CPI_YOY 2023-09 | series_store CN_CPI_YOY@2023-09 | 0.0 | 0.0 | 一致 |  |
| 852 | 2023-10 latest visible CN_CPI_YOY at 2023-10-31 | series_store + seat rule = 2023-09-01 (pub 2023-10-09) | 2023-09 | 2023-09 | 一致 |  |
| 853 | 2023-10 sync labels present | judgment other_regions_sync | 中国分化、欧元区分化、日本分化 | —(仅席位直算) | 信息行(不计入) | informational: 标签三联在场(逐格比对见 sync 节 judgment 行) |
| 854 | 2023-10 coverage growth | report.json state_vector.growth.coverage | 0.1667 | 0.17 | 一致 |  |
| 855 | 2023-10 coverage inflation | report.json state_vector.inflation.coverage | 0.3333 | 0.33 | 一致 |  |
| 856 | 2023-10 coverage credit | report.json state_vector.credit.coverage | 0.5 | 0.5 | 一致 |  |
| 857 | C2 2025-03 3m DXY negative | judgment ex_post 3m | -7.03 | <0 | 一致 |  |
| 858 | C2 2025-03 3m GOLD_F positive | judgment ex_post 3m | 5.92 | >0 | 一致 |  |
| 859 | C2 2022-06 3m equities all negative | judgment ex_post 3m | SPX-5.28 NIKKEI225-1.73 DAX-5.24 SHCOMP-11.01 | all negative | 一致 |  |
| 860 | C2 2022-06 12m equities positive except SHCOMP | judgment ex_post 12m | SPX+17.57 NIKKEI225+25.75 DAX+26.32 SHCOMP-5.78 | SHCOMP<0, others>0 | 一致 |  |
| 861 | C2 2023-10 3m DXY negative | judgment ex_post 3m | -3.18 | <0 | 一致 |  |
| 862 | C2 2023-10 3m GOLD_F positive | judgment ex_post 3m | 2.71 | >0 | 一致 |  |
| 863 | C2 2023-10 3m SHCOMP negative (exception) | judgment ex_post 3m | -7.63 | <0 | 一致 |  |
| 864 | sign agreement SPX 1m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 865 | sign agreement SPX 3m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 866 | sign agreement SPX 3m between 0.6 and 0.8 (C2 claim) | recompute | 0.6 | 0.6..0.8 | 一致 |  |
| 867 | sign agreement SPX 6m | series_store recompute over 5 cluster representatives | 1.0 | 1.0 | 一致 | engine dispersion face |
| 868 | sign agreement SPX 6m = 1.0 (C2 claim) | recompute | 1.0 | 1.0 | 一致 |  |
| 869 | sign agreement SPX 12m | series_store recompute over 5 cluster representatives | 1.0 | 1.0 | 一致 | engine dispersion face |
| 870 | sign agreement SPX 12m = 1.0 (C2 claim) | recompute | 1.0 | 1.0 | 一致 |  |
| 871 | sign agreement UST_10Y 1m | series_store recompute over 5 cluster representatives | 0.8 | 0.8 | 一致 | engine dispersion face |
| 872 | sign agreement UST_10Y 1m between 0.6 and 0.8 (C2 claim) | recompute | 0.8 | 0.6..0.8 | 一致 |  |
| 873 | sign agreement UST_10Y 3m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 874 | sign agreement UST_10Y 3m between 0.6 and 0.8 (C2 claim) | recompute | 0.6 | 0.6..0.8 | 一致 |  |
| 875 | sign agreement UST_10Y 6m | series_store recompute over 5 cluster representatives | 0.8 | 0.8 | 一致 | engine dispersion face |
| 876 | sign agreement UST_10Y 6m between 0.6 and 0.8 (C2 claim) | recompute | 0.8 | 0.6..0.8 | 一致 |  |
| 877 | sign agreement UST_10Y 12m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 878 | sign agreement UST_10Y 12m between 0.6 and 0.8 (C2 claim) | recompute | 0.6 | 0.6..0.8 | 一致 |  |
| 879 | sign agreement DXY 1m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 880 | sign agreement DXY 3m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 881 | sign agreement DXY 6m | series_store recompute over 5 cluster representatives | 0.8 | 0.8 | 一致 | engine dispersion face |
| 882 | sign agreement DXY 12m | series_store recompute over 5 cluster representatives | 0.8 | 0.8 | 一致 | engine dispersion face |
| 883 | sign agreement GOLD_F 1m | series_store recompute over 5 cluster representatives | 0.6 | 0.6 | 一致 | engine dispersion face |
| 884 | sign agreement GOLD_F 3m | series_store recompute over 5 cluster representatives | 0.8 | 0.8 | 一致 | engine dispersion face |
| 885 | sign agreement GOLD_F 3m between 0.6 and 0.8 (C2 claim) | recompute | 0.8 | 0.6..0.8 | 一致 |  |
| 886 | sign agreement GOLD_F 6m | series_store recompute over 5 cluster representatives | 1.0 | 1.0 | 一致 | engine dispersion face |
| 887 | sign agreement GOLD_F 6m = 1.0 (C2 claim) | recompute | 1.0 | 1.0 | 一致 |  |
| 888 | sign agreement GOLD_F 12m | series_store recompute over 5 cluster representatives | 1.0 | 1.0 | 一致 | engine dispersion face |
| 889 | sign agreement GOLD_F 12m = 1.0 (C2 claim) | recompute | 1.0 | 1.0 | 一致 |  |
| 890 | candidates scanned/valid/dropped | report.json candidates | 1871/74/12/1785 | 1871/74/12/1785 | 一致 |  |
| 891 | n independent clusters | report.json candidates.n_independent_clusters_topN | 5 | 5 | 一致 | TOP-5独立簇 |
| 892 | C2 2025-03 risk assets & GOLD_F windows positive (5 metrics x 3/6/12m) | series_store 2025-03 月末→锚+N月月末,逐值与台账 history 行对账 \| agent_judgment.json l3.contradictions[1].statement | 15/15 | 多数窗走强 | 一致 | SPX/NIKKEI225/DAX/SHCOMP/GOLD_F × 3/6/12 月,月末口径,直算自 series_store |
| 893 | C2 2025-03 DXY negative in 3/6/12m windows | series_store DXY 2025-03 月末→锚+3/6/12月月末 \| agent_judgment.json l3.contradictions[1].statement「DXY 走弱」 | 3/3 | DXY 走弱 | 一致 | -7.03 -6.18 -4.08 |
| 894 | C2 2023-10 risk assets & GOLD_F windows positive (5 metrics x 3/6/12m) | series_store 2023-10 月末→锚+N月月末,逐值与台账 history 行对账 \| agent_judgment.json l3.contradictions[1].statement | 14/15 (SHCOMP 3m -7.63) | 多数窗走强(2023-10段上证指数三个月窗为负,属例外) | 一致 | 例外窗=2023-10段上证三个月窗,与陈述括注一致 |
| 895 | C2 2023-10 DXY negative in 3/6/12m windows | series_store DXY 2023-10 月末→锚+3/6/12月月末 \| agent_judgment.json l3.contradictions[1].statement「DXY 走弱」 | 3/3 | DXY 走弱 | 一致 | -3.18 -0.41 -2.51 |

#### 1.2.5 同步面(计点 45 行: 一致 45、偏离 0;信息行 36)

| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|---|
| 896 | sync 2025-03 US growth label | series_store + seat visibility rule | 下行 | 下行 | 一致 | engine face label |
| 897 | sync 2025-03 US growth direction | series_store + seat visibility rule | -0.306 | —(仅席位直算) | 信息行(不计入) | engine: US growth 下行 |
| 898 | sync 2025-03 US inflation label | series_store + seat visibility rule | 上行 | 上行 | 一致 | engine face label |
| 899 | sync 2025-03 US inflation direction | series_store + seat visibility rule | 0.08211 | —(仅席位直算) | 信息行(不计入) | engine: US inflation 上行 |
| 900 | sync 2025-03 US policy label | series_store + seat visibility rule | 持平 | 持平 | 一致 | engine face label |
| 901 | sync 2025-03 US policy direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: US policy 持平 |
| 902 | sync 2025-03 CN growth label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 903 | sync 2025-03 CN growth direction | series_store + seat visibility rule | 0.4 | —(仅席位直算) | 信息行(不计入) | engine: CN growth 分化 |
| 904 | sync 2025-03 CN inflation label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 905 | sync 2025-03 CN inflation direction | series_store + seat visibility rule | -0.9 | —(仅席位直算) | 信息行(不计入) | engine: CN inflation 分化 |
| 906 | sync 2025-03 CN policy label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 907 | sync 2025-03 CN policy direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: CN policy 同步 |
| 908 | sync 2025-03 EA growth label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 909 | sync 2025-03 EA growth direction | series_store + seat visibility rule | 0.25 | —(仅席位直算) | 信息行(不计入) | engine: EA growth 分化 |
| 910 | sync 2025-03 EA inflation label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 911 | sync 2025-03 EA inflation direction | series_store + seat visibility rule | -0.1 | —(仅席位直算) | 信息行(不计入) | engine: EA inflation 分化 |
| 912 | sync 2025-03 EA policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 913 | sync 2025-03 EA policy direction | series_store + seat visibility rule | -0.5 | —(仅席位直算) | 信息行(不计入) | engine: EA policy 分化 |
| 914 | sync 2025-03 JP growth label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 915 | sync 2025-03 JP growth direction | series_store + seat visibility rule | -0.1 | —(仅席位直算) | 信息行(不计入) | engine: JP growth 同步 |
| 916 | sync 2025-03 JP inflation label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 917 | sync 2025-03 JP inflation direction | series_store + seat visibility rule | 0.74 | —(仅席位直算) | 信息行(不计入) | engine: JP inflation 同步 |
| 918 | sync 2025-03 JP policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 919 | sync 2025-03 JP policy direction | series_store + seat visibility rule | 0.251 | —(仅席位直算) | 信息行(不计入) | engine: JP policy 分化 |
| 920 | sync 2022-06 US growth label | series_store + seat visibility rule | 下行 | 下行 | 一致 | engine face label |
| 921 | sync 2022-06 US growth direction | series_store + seat visibility rule | -1.843 | —(仅席位直算) | 信息行(不计入) | engine: US growth 下行 |
| 922 | sync 2022-06 US inflation label | series_store + seat visibility rule | 上行 | 上行 | 一致 | engine face label |
| 923 | sync 2022-06 US inflation direction | series_store + seat visibility rule | 0.6009 | —(仅席位直算) | 信息行(不计入) | engine: US inflation 上行 |
| 924 | sync 2022-06 US policy label | series_store + seat visibility rule | 上行 | 上行 | 一致 | engine face label |
| 925 | sync 2022-06 US policy direction | series_store + seat visibility rule | 1.25 | —(仅席位直算) | 信息行(不计入) | engine: US policy 上行 |
| 926 | sync 2022-06 CN growth label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 927 | sync 2022-06 CN growth direction | series_store + seat visibility rule | 0.7 | —(仅席位直算) | 信息行(不计入) | engine: CN growth 分化 |
| 928 | sync 2022-06 CN inflation label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 929 | sync 2022-06 CN inflation direction | series_store + seat visibility rule | 1.2 | —(仅席位直算) | 信息行(不计入) | engine: CN inflation 同步 |
| 930 | sync 2022-06 CN policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 931 | sync 2022-06 CN policy direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: CN policy 分化 |
| 932 | sync 2022-06 EA growth label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 933 | sync 2022-06 EA growth direction | series_store + seat visibility rule | -0.1 | —(仅席位直算) | 信息行(不计入) | engine: EA growth 同步 |
| 934 | sync 2022-06 EA inflation label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 935 | sync 2022-06 EA inflation direction | series_store + seat visibility rule | 0.7 | —(仅席位直算) | 信息行(不计入) | engine: EA inflation 同步 |
| 936 | sync 2022-06 EA policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 937 | sync 2022-06 EA policy direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: EA policy 分化 |
| 938 | sync 2022-06 JP growth label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 939 | sync 2022-06 JP growth direction | series_store + seat visibility rule | -1.65 | —(仅席位直算) | 信息行(不计入) | engine: JP growth 同步 |
| 940 | sync 2022-06 JP inflation label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 941 | sync 2022-06 JP inflation direction | series_store + seat visibility rule | 1.51 | —(仅席位直算) | 信息行(不计入) | engine: JP inflation 同步 |
| 942 | sync 2022-06 JP policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 943 | sync 2022-06 JP policy direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: JP policy 分化 |
| 944 | sync 2023-10 US growth label | series_store + seat visibility rule | 上行 | 上行 | 一致 | engine face label |
| 945 | sync 2023-10 US growth direction | series_store + seat visibility rule | 0.4479 | —(仅席位直算) | 信息行(不计入) | engine: US growth 上行 |
| 946 | sync 2023-10 US inflation label | series_store + seat visibility rule | 上行 | 上行 | 一致 | engine face label |
| 947 | sync 2023-10 US inflation direction | series_store + seat visibility rule | 0.6166 | —(仅席位直算) | 信息行(不计入) | engine: US inflation 上行 |
| 948 | sync 2023-10 US policy label | series_store + seat visibility rule | 持平 | 持平 | 一致 | engine face label |
| 949 | sync 2023-10 US policy direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: US policy 持平 |
| 950 | sync 2023-10 CN growth label | series_store + seat visibility rule | 同步 | 同步 | 一致 | engine face label |
| 951 | sync 2023-10 CN growth direction | series_store + seat visibility rule | 0.2 | —(仅席位直算) | 信息行(不计入) | engine: CN growth 同步 |
| 952 | sync 2023-10 CN inflation label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 953 | sync 2023-10 CN inflation direction | series_store + seat visibility rule | 0 | —(仅席位直算) | 信息行(不计入) | engine: CN inflation 分化 |
| 954 | sync 2023-10 CN policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 955 | sync 2023-10 CN policy direction | series_store + seat visibility rule | -0.1 | —(仅席位直算) | 信息行(不计入) | engine: CN policy 分化 |
| 956 | sync 2023-10 EA growth label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 957 | sync 2023-10 EA growth direction | series_store + seat visibility rule | -0.74 | —(仅席位直算) | 信息行(不计入) | engine: EA growth 分化 |
| 958 | sync 2023-10 EA inflation label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 959 | sync 2023-10 EA inflation direction | series_store + seat visibility rule | -2.4 | —(仅席位直算) | 信息行(不计入) | engine: EA inflation 分化 |
| 960 | sync 2023-10 EA policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 961 | sync 2023-10 EA policy direction | series_store + seat visibility rule | 0.5 | —(仅席位直算) | 信息行(不计入) | engine: EA policy 分化 |
| 962 | sync 2023-10 JP growth label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 963 | sync 2023-10 JP growth direction | series_store + seat visibility rule | -0.89 | —(仅席位直算) | 信息行(不计入) | engine: JP growth 分化 |
| 964 | sync 2023-10 JP inflation label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 965 | sync 2023-10 JP inflation direction | series_store + seat visibility rule | -0.25 | —(仅席位直算) | 信息行(不计入) | engine: JP inflation 分化 |
| 966 | sync 2023-10 JP policy label | series_store + seat visibility rule | 分化 | 分化 | 一致 | engine face label |
| 967 | sync 2023-10 JP policy direction | series_store + seat visibility rule | 0.012 | —(仅席位直算) | 信息行(不计入) | engine: JP policy 分化 |
| 968 | sync 2025-03 judgment CN inflation label | MAP_REPORT.md L344 地区×维度同步面(引擎确定性面) | 分化 | 分化 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 部分同步) |
| 969 | sync 2025-03 judgment EA inflation label | MAP_REPORT.md L347 地区×维度同步面(引擎确定性面) | 分化 | 分化 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 部分同步) |
| 970 | sync 2025-03 judgment JP inflation label | MAP_REPORT.md L350 地区×维度同步面(引擎确定性面) | 同步 | 同步 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 部分同步) |
| 971 | sync 2022-06 judgment CN inflation label | MAP_REPORT.md L462 地区×维度同步面(引擎确定性面) | 同步 | 同步 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 同步) |
| 972 | sync 2022-06 judgment EA inflation label | MAP_REPORT.md L465 地区×维度同步面(引擎确定性面) | 同步 | 同步 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 同步) |
| 973 | sync 2022-06 judgment JP inflation label | MAP_REPORT.md L468 地区×维度同步面(引擎确定性面) | 同步 | 同步 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 同步) |
| 974 | sync 2023-10 judgment CN inflation label | MAP_REPORT.md L586 地区×维度同步面(引擎确定性面) | 分化 | 分化 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 不同步) |
| 975 | sync 2023-10 judgment EA inflation label | MAP_REPORT.md L589 地区×维度同步面(引擎确定性面) | 分化 | 分化 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 不同步) |
| 976 | sync 2023-10 judgment JP inflation label | MAP_REPORT.md L592 地区×维度同步面(引擎确定性面) | 分化 | 分化 | 一致 | 判断档 other_regions_sync 通胀维标签 vs 引擎面(引导词 不同步) |

#### 1.2.6 其他(计点 69 行: 一致 69、偏离 0;信息行 4)

| # | 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|---|
| 977 | Gate A status | snapshot gate_a | DEGRADED | DEGRADED | 一致 | judgment: 本轮 Gate A 判 DEGRADED |
| 978 | Gate A core_missing count | snapshot gate_a.core_missing | 0 | 0 | 一致 |  |
| 979 | Gate A noncore_missing count | snapshot gate_a.noncore_missing | 7 | 7 | 一致 |  |
| 980 | Gate A noncore_degraded count | snapshot gate_a.noncore_degraded | 8 | 8 | 一致 |  |
| 981 | Gate A noncore missing metrics with stock observations | snapshot gate_a.noncore_missing x series_store | 5: CN_OMO_7D CN_POLICY_OVERNIGHT EA_REAL_GDP_YOY JP_CPI_TOKYO_YOY JP_REAL_GDP_YOY | 5 | 一致 | 缺口指标中有五项在序列库内仍有存量观测 |
| 982 | all unique evidence refs point to an observation | judgment evidence_refs x series_store | ∅(空串) | none unresolved | 一致 | n_unique=20 |
| 983 | evidence refs count, L3 scope (contradictions + mechanism chains) | agent_judgment l3.*.evidence_refs | 41 | 41 | 一致 | quality note says 证据引用共 41 条 without naming the scope; L4 scenarios add 9 more refs (total 50) |
| 984 | turning[0] CPI before | series_store CPI@2026-02 | 2.434 | 2.434 | 一致 |  |
| 985 | turning[0] CPI after | series_store CPI@2026-05 | 4.1666 | 4.1666 | 一致 |  |
| 986 | turning[0] CPI window | judgment turnings | 2026-02→2026-05 | —(仅席位直算) | 信息行(不计入) | dimension=inflation |
| 987 | turning[1] INDPRO before | series_store INDPRO@2025-11 | 1.7543 | 1.7543 | 一致 |  |
| 988 | turning[1] INDPRO after | series_store INDPRO@2026-02 | 0.7972 | 0.7972 | 一致 |  |
| 989 | turning[1] INDPRO window | judgment turnings | 2025-11→2026-02 | —(仅席位直算) | 信息行(不计入) | dimension=growth |
| 990 | turning[2] JP_CPI_YOY before | series_store JP_CPI_YOY@2025-11 | 2.9 | 2.9 | 一致 |  |
| 991 | turning[2] JP_CPI_YOY after | series_store JP_CPI_YOY@2026-02 | 1.27 | 1.27 | 一致 |  |
| 992 | turning[2] JP_CPI_YOY window | judgment turnings | 2025-11→2026-02 | —(仅席位直算) | 信息行(不计入) | dimension=inflation |
| 993 | turning supplement JP_CPI_TOKYO_YOY from | series_store JP_CPI_TOKYO_YOY@2026-06 | 1.6 | 1.6 | 一致 |  |
| 994 | turning supplement JP_CPI_TOKYO_YOY to | series_store JP_CPI_TOKYO_YOY@2026-09 | 2.69 | 2.69 | 一致 |  |
| 995 | candidate CN_CPI_YOY 2026-01 | series_store CN_CPI_YOY@2026-01 | 0.2 | 0.2 | 一致 |  |
| 996 | candidate CN_PPI_YOY 2026-02 | series_store CN_PPI_YOY@2026-02 | -0.9 | -0.9 | 一致 |  |
| 997 | evidence ref CPI@2026-10-01 | agent_judgment.json l3.contradictions[0].evidence_refs[0] 等共 2 处 \| evidence_index.json ref \| series_store CPI | 观测 2026-10-01=337.476 | CPI@2026-10-01(证据索引在列=True) | 一致 |  |
| 998 | evidence ref CORE_PCE@2026-09-01 | agent_judgment.json l3.contradictions[0].evidence_refs[1] 等共 2 处 \| evidence_index.json ref \| series_store CORE_PCE | 观测 2026-09-01=130.902 | CORE_PCE@2026-09-01(证据索引在列=True) | 一致 |  |
| 999 | evidence ref EA_HICP_YOY@2026-10-01 | agent_judgment.json l3.contradictions[0].evidence_refs[2] 等共 2 处 \| evidence_index.json ref \| series_store EA_HICP_YOY | 观测 2026-10-01=4.0 | EA_HICP_YOY@2026-10-01(证据索引在列=True) | 一致 |  |
| 1000 | evidence ref CN_PPI_YOY@2026-10-31 | agent_judgment.json l3.contradictions[0].evidence_refs[3] 等共 3 处 \| evidence_index.json ref \| series_store CN_PPI_YOY | 观测 2026-10-01=5.7 | CN_PPI_YOY@2026-10-31(证据索引在列=True) | 一致 | 标签日=观测月末,序列观测日=月初(同一观测两个日期标签;判断档 quality_gate_notes[5]-④ 已披露) |
| 1001 | evidence ref DFF@2026-11-19 | agent_judgment.json l3.contradictions[0].evidence_refs[4] 等共 1 处 \| evidence_index.json ref \| series_store DFF | 观测 2026-11-19=3.88 | DFF@2026-11-19(证据索引在列=True) | 一致 |  |
| 1002 | evidence ref ECB_DFR@2026-09-16 | agent_judgment.json l3.contradictions[0].evidence_refs[5] 等共 1 处 \| evidence_index.json ref \| series_store ECB_DFR | 观测 2026-09-16=2.5 | ECB_DFR@2026-09-16(证据索引在列=True) | 一致 |  |
| 1003 | evidence ref JP_POLICY_RATE@2026-10-01 | agent_judgment.json l3.contradictions[0].evidence_refs[6] 等共 2 处 \| evidence_index.json ref \| series_store JP_POLICY_RATE | 观测 2026-10-01=1.227 | JP_POLICY_RATE@2026-10-01(证据索引在列=True) | 一致 |  |
| 1004 | evidence ref UST_10Y@2026-11-19 | agent_judgment.json l3.contradictions[0].evidence_refs[7] 等共 3 处 \| evidence_index.json ref \| series_store UST_10Y | 观测 2026-11-19=5.04 | UST_10Y@2026-11-19(证据索引在列=True) | 一致 |  |
| 1005 | evidence ref TIPS_10Y@2026-11-19 | agent_judgment.json l3.contradictions[0].evidence_refs[8] 等共 4 处 \| evidence_index.json ref \| series_store TIPS_10Y | 观测 2026-11-19=2.88 | TIPS_10Y@2026-11-19(证据索引在列=True) | 一致 |  |
| 1006 | evidence ref BEI_10Y@2026-11-20 | agent_judgment.json l3.contradictions[0].evidence_refs[9] 等共 3 处 \| evidence_index.json ref \| series_store BEI_10Y | 观测 2026-11-20=2.15 | BEI_10Y@2026-11-20(证据索引在列=True) | 一致 |  |
| 1007 | evidence ref SPX@2026-11-23 | agent_judgment.json l3.contradictions[0].evidence_refs[10] 等共 5 处 \| evidence_index.json ref \| series_store SPX | 观测 2026-11-23=7203.850098 | SPX@2026-11-23(证据索引在列=True) | 一致 |  |
| 1008 | evidence ref NIKKEI225@2026-11-20 | agent_judgment.json l3.contradictions[0].evidence_refs[11] 等共 2 处 \| evidence_index.json ref \| series_store NIKKEI225 | 观测 2026-11-20=56436.65 | NIKKEI225@2026-11-20(证据索引在列=True) | 一致 |  |
| 1009 | evidence ref GOLD_F@2026-11-23 | agent_judgment.json l3.contradictions[0].evidence_refs[12] 等共 5 处 \| evidence_index.json ref \| series_store GOLD_F | 观测 2026-11-23=3685.199951 | GOLD_F@2026-11-23(证据索引在列=True) | 一致 |  |
| 1010 | evidence ref DXY@2026-11-23 | agent_judgment.json l3.contradictions[0].evidence_refs[13] 等共 5 处 \| evidence_index.json ref \| series_store DXY | 观测 2026-11-23=104.079002 | DXY@2026-11-23(证据索引在列=True) | 一致 |  |
| 1011 | evidence ref VIX@2026-11-23 | agent_judgment.json l3.contradictions[0].evidence_refs[14] 等共 3 处 \| evidence_index.json ref \| series_store VIX | 观测 2026-11-23=27.01 | VIX@2026-11-23(证据索引在列=True) | 一致 |  |
| 1012 | evidence ref HY_OAS@2026-11-19 | agent_judgment.json l3.contradictions[0].evidence_refs[15] 等共 2 处 \| evidence_index.json ref \| series_store HY_OAS | 观测 2026-11-19=3.52 | HY_OAS@2026-11-19(证据索引在列=True) | 一致 |  |
| 1013 | evidence ref USDJPY@2026-11-23 | agent_judgment.json l3.contradictions[0].evidence_refs[16] 等共 2 处 \| evidence_index.json ref \| series_store USDJPY | 观测 2026-11-23=159.347 | USDJPY@2026-11-23(证据索引在列=True) | 一致 |  |
| 1014 | evidence ref CN_CPI_YOY@2026-10-31 | agent_judgment.json l3.contradictions[2].evidence_refs[1] 等共 1 处 \| evidence_index.json ref \| series_store CN_CPI_YOY | 观测 2026-10-01=0.7 | CN_CPI_YOY@2026-10-31(证据索引在列=True) | 一致 | 标签日=观测月末,序列观测日=月初(同一观测两个日期标签;判断档 quality_gate_notes[5]-④ 已披露) |
| 1015 | evidence ref CN_LPR_1Y@2026-11-20 | agent_judgment.json l3.contradictions[2].evidence_refs[2] 等共 1 处 \| evidence_index.json ref \| series_store CN_LPR_1Y | 观测 2026-11-20=3.0 | CN_LPR_1Y@2026-11-20(证据索引在列=True) | 一致 |  |
| 1016 | evidence ref USDCNY@2026-11-23 | agent_judgment.json l3.contradictions[2].evidence_refs[3] 等共 1 处 \| evidence_index.json ref \| series_store USDCNY | 观测 2026-11-23=6.6542 | USDCNY@2026-11-23(证据索引在列=True) | 一致 |  |
| 1017 | policy BoJ decision date | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].decision_date \| agent_judgment.json 「决议2026-09-18」 | 2026-09-18 | 2026-09-18 | 一致 | 冻结日历实录条目(非回推) |
| 1018 | policy BoJ effective date | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].effective_on \| agent_judgment.json 「生效2026-09-24」 | 2026-09-24 | 2026-09-24 | 一致 |  |
| 1019 | policy BoJ official target value | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].target_value \| agent_judgment.json | 1.25 | 1.25 | 一致 | 判断档含该表述=True |
| 1020 | policy Japan latest maintenance decision date | release_calendar.json entries[RC-JP-BOJ-MAINT-2026-10].decision_date \| MAP_REPORT.md 政策官方记录面「最近确认维持」 | 2026-10-30 | 2026-10-30 | 一致 |  |
| 1021 | policy Japan verification coverage end | release_calendar.json latest JP_POLICY_TARGET entry with decision_date <= cutoff \| MAP_REPORT.md 「核验覆盖截止」 | 2026-10-30 | 2026-10-30 | 一致 |  |
| 1022 | policy Japan days since last change (by effective date) | (2026-11-23 − 2026-09-24) days \| MAP_REPORT.md 「距上次调整(按生效日)」 | 60 | 60 | 一致 | 判断档未给出天数 |
| 1023 | policy Japan days since decision | (2026-11-23 − 2026-09-18) days \| MAP_REPORT.md 「距决议」 | 66 | 66 | 一致 | 判断档未给出天数 |
| 1024 | policy Japan days since maintenance | (2026-11-23 − 2026-10-30) days \| MAP_REPORT.md 「距维持」 | 24 | 24 | 一致 | 判断档未给出天数 |
| 1025 | policy pending decision effective after cutoff | release_calendar.json policy_decision entries with effective_on > 2026-11-23 \| MAP_REPORT.md 「待生效」 | True | True | 一致 | True=无待生效决定(表内记「—」);无待生效决定则现行目标与官方目标同值 |
| 1026 | policy calendar has no Fed/ECB record entries | release_calendar.json entries metric_id scan \| agent_judgment.json quality_gate_notes[2] | True | True | 一致 | 命中条目=[] |
| 1027 | policy decision date POLCLUSTER-01 US DFEDTARU (convention back-calculation) | series_store DFEDTARU value-change date 2025-12-11 + engine convention (2025-12-10 -> 2025-12-11) \| report.json policy_event_clusters \| judgment contains date=True | 2025-12-10 | 2025-12-10 | 一致 | 判断档标【推断】 |
| 1028 | policy effective date POLCLUSTER-01 US DFEDTARU (= series change date) | series_store DFEDTARU value-change date \| report.json policy_event_clusters.events.effective_date | 2025-12-11 | 2025-12-11 | 一致 | 判断档含该生效日=True |
| 1029 | policy value before POLCLUSTER-01 US DFEDTARU | series_store DFEDTARU value before change | 4.0 | 4.0 | 一致 |  |
| 1030 | policy value after POLCLUSTER-01 US DFEDTARU | series_store DFEDTARU value after change | 3.75 | 3.75 | 一致 |  |
| 1031 | policy decision date POLCLUSTER-02 EA ECB_DFR (convention back-calculation) | series_store ECB_DFR value-change date 2026-06-17 + engine convention (2026-06-11 -> 2026-06-17) \| report.json policy_event_clusters \| judgment contains date=True | 2026-06-11 | 2026-06-11 | 一致 | 判断档标【推断】 |
| 1032 | policy effective date POLCLUSTER-02 EA ECB_DFR (= series change date) | series_store ECB_DFR value-change date \| report.json policy_event_clusters.events.effective_date | 2026-06-17 | 2026-06-17 | 一致 | 判断档含该生效日=True |
| 1033 | policy value before POLCLUSTER-02 EA ECB_DFR | series_store ECB_DFR value before change | 2.0 | 2.0 | 一致 |  |
| 1034 | policy value after POLCLUSTER-02 EA ECB_DFR | series_store ECB_DFR value after change | 2.25 | 2.25 | 一致 |  |
| 1035 | policy decision date POLCLUSTER-03 EA ECB_DFR (convention back-calculation) | series_store ECB_DFR value-change date 2026-09-16 + engine convention (2026-09-10 -> 2026-09-16) \| report.json policy_event_clusters \| judgment contains date=True | 2026-09-10 | 2026-09-10 | 一致 | 判断档标【推断】 |
| 1036 | policy effective date POLCLUSTER-03 EA ECB_DFR (= series change date) | series_store ECB_DFR value-change date \| report.json policy_event_clusters.events.effective_date | 2026-09-16 | 2026-09-16 | 一致 | 判断档含该生效日=True |
| 1037 | policy value before POLCLUSTER-03 EA ECB_DFR | series_store ECB_DFR value before change | 2.25 | 2.25 | 一致 |  |
| 1038 | policy value after POLCLUSTER-03 EA ECB_DFR | series_store ECB_DFR value after change | 2.5 | 2.5 | 一致 |  |
| 1039 | policy decision date POLCLUSTER-03 US DFEDTARU (convention back-calculation) | series_store DFEDTARU value-change date 2026-09-17 + engine convention (2026-09-16 -> 2026-09-17) \| report.json policy_event_clusters \| judgment contains date=True | 2026-09-16 | 2026-09-16 | 一致 | 判断档标【推断】 |
| 1040 | policy effective date POLCLUSTER-03 US DFEDTARU (= series change date) | series_store DFEDTARU value-change date \| report.json policy_event_clusters.events.effective_date | 2026-09-17 | 2026-09-17 | 一致 | 判断档含该生效日=True |
| 1041 | policy value before POLCLUSTER-03 US DFEDTARU | series_store DFEDTARU value before change | 3.75 | 3.75 | 一致 |  |
| 1042 | policy value after POLCLUSTER-03 US DFEDTARU | series_store DFEDTARU value after change | 4.0 | 4.0 | 一致 |  |
| 1043 | policy lag to research cutoff: 2026-09-16 | (2026-11-23 − 2026-09-16) days \| MAP_REPORT.md L97,100 「距研究截止」 | 68 | 68 | 一致 |  |
| 1044 | policy lag to research cutoff: 2026-09-17 | (2026-11-23 − 2026-09-17) days \| MAP_REPORT.md L106 「距研究截止」 | 67 | 67 | 一致 |  |
| 1045 | policy lag to research cutoff: 2026-10-30 | (2026-11-23 − 2026-10-30) days \| MAP_REPORT.md L93 「距研究截止」 | 24 | 24 | 一致 |  |
| 1046 | policy lag to research cutoff: 2026-11-19 | (2026-11-23 − 2026-11-19) days \| MAP_REPORT.md L109 「距研究截止」 | 4 | 4 | 一致 |  |
| 1047 | policy lag to research cutoff: 2026-11-20 | (2026-11-23 − 2026-11-20) days \| MAP_REPORT.md L90 「距研究截止」 | 3 | 3 | 一致 |  |
| 1048 | policy lag to research cutoff: 2026-11-23 | (2026-11-23 − 2026-11-23) days \| MAP_REPORT.md L94 「距研究截止」 | 0 | 0 | 一致 |  |
| 1049 | policy days since last change at cutoff (US by effective date / EA by effective date / JP by effective date) | seat arithmetic from series change dates and calendar effective_on | US 67 / EA 68 / JP 60 | —(仅席位直算) | 信息行(不计入) | 判断档未给出天数,仅作信息记录 |

## 2. 规程第 4 节: 六查逐项结论

审查对象逐条: l3.contradictions[0](C1 主线综合)、[1](C2 历史相似段的证据冲突)、[2](C3 中国政策背离);l3.mechanism_chains[0] 四环(M1-1 冲击环、M1-2 政策环、M1-3 利率环、M1-4 资产环)与 l3.mechanism_chains[1] 两环(M2-1、M2-2)。六查 = 证据相关性 / 支持度 / 竞争解释 / 反对证据 / 结论是否超出证据 / 证伪条件可观测性。结论用词: 通过;部分通过(指向第 6 节编号);通过(注明)。本节只写值,逐点出处见第 1.2 节台账。

### 2.1 C1 主线综合(通胀再加速→政策再收紧→实际利率上行→风险资产收缩的同向共动)

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | 陈述末尾 11 个水平值逐一在 series_store 命中: UST_10Y 5.04@2026-11-19、TIPS_10Y 2.88@2026-11-19、BEI_10Y 2.15@2026-11-20、VIX 27.01@2026-11-23、HY_OAS 3.52@2026-11-19、USDJPY 159.35(库值 159.347)@2026-11-23、DFF 3.88@2026-11-19、JP_POLICY_RATE 1.227@2026-10-01、CN_PPI_YOY 5.7@2026-10-01、CN_CPI_YOY 0.7@2026-10-01、CN_PMI_MFG 49.3@2026-10-01;17 处证据引用全部在本轮证据索引内。 |
| 支持度 | 通过(注明) | 四段方向各有序列支撑: 通胀再加速(CPI 同比 2.434@2026-02→4.1666@2026-05;EA_HICP_YOY 1.9→3.2;CN_PPI_YOY −0.9→3.9);政策再收紧(ECB_DFR 2.0→2.25→2.5;DFEDTARU 3.75→4.0;JP_POLICY_RATE 月均 0.478@2025-11→1.227@2026-10);实际利率上行(TIPS_10Y 12 个月 +102bp);近月风险资产收缩(SPX −5.51%、NIKKEI225 −9.98%、GOLD_F −8.05%,VIX 19.45→27.01)。制造业PMI「五个月站上荣枯线」=2025-12、2026-03、2026-04、2026-06、2026-09(50.1/50.4/50.3/50.3/50.1),其余月份 49.0–50.0,与序列一致。注明: 「同向共动」只在近月窗成立——12 个月窗 SPX +8.03%、NIKKEI225 +22.47% 与实际利率同向上行,陈述未披露(第 4 节攻击 5,MINOR-3)。 |
| 竞争解释 | 通过 | A/B/C 三种解释对同一组指标给出互异预期: A『实际利率主导』=BEI_10Y 大体稳定而 TIPS_10Y 续升;B『增长担忧』=BEI_10Y 主导性下行而 TIPS_10Y 转平或回落;C『溢出/技术面』=USDJPY 与风险资产波动在时间上更紧耦合且 HY_OAS 平稳。均为可对质表述,不是同义改写。 |
| 反对证据 | 通过(注明) | 近 1 个月共同交易日(2026-10-20→2026-11-19)TIPS_10Y +11bp(合 A)与 BEI_10Y −19bp(合 B)并存,解释B正文如实写明;同窗 USDJPY +1.82%(156.494→159.347)而 SPX −5.51%,与 C 的「更紧耦合」预期相左,陈述未把 C 写成成立。 |
| 结论是否超出证据 | 通过 | 结论句明写「当前证据不足以在它们之间裁决」,头条结论句标「(描述,非预测)」;无因果断言或外推。 |
| 证伪条件可观测性 | 通过 | 区分指标 BEI_10Y、TIPS_10Y、HY_OAS、USDJPY 全部在库且更新至截止日附近(末观测 2026-11-20/19/19/23);数值阈值在传导面与情景面给出(见 2.4、2.5、3.3)。 |

### 2.2 C2 历史相似段的证据冲突

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | 所引四项(SPX、UST_10Y、GOLD_F、DXY@2026-11-23)在陈述中明示为「四项资产的当前水平锚点」,不承载历史数字;历史段数字取自引擎相似检索面事后块。 |
| 支持度 | 通过 | 事后值按月末口径复算 99 值全中(11 个指标 × 3/6/12 月 × 三段);符号一致率 SPX 0.6/0.6/1.0/1.0、UST_10Y 0.8/0.6/0.8/0.6、DXY 0.6/0.6/0.8/0.8、GOLD_F 0.6/0.8/1.0/1.0 与引擎面一致;「GOLD_F 与 SPX 六个月与十二个月窗符号一致」成立(两者均为 1.0),「其余各窗 0.6–0.8」成立;方向归纳逐窗核对成立: 2022-06 段三个月窗四地股指均为负(SPX −5.28、NIKKEI225 −1.73、DAX −5.24、SHCOMP −11.01)、十二个月窗除上证外转正(+17.57/+25.75/+26.32,上证 −5.78);2025-03、2023-10 段风险资产与 GOLD_F 多数窗走强(五个指标×三窗: 2025-03 段 15/15 为正,2023-10 段 14/15,例外即上证三个月窗 −7.63);两段 DXY 走弱(各 3/3 窗为负)。 |
| 竞争解释 | 通过(注明) | A=各自独有的政策/冲击环境(事件叙述,自标【假设】);B=相似度量的低维覆盖(0.17/0.33/0.5 与引擎面一致)。两者可区分,但本引擎无法检验——陈述未据此下结论。 |
| 反对证据 | 通过 | 陈述本身即以「事后路径分歧」作为反对「可外推」的证据,并自己列出了例外(2023-10 上证三个月窗为负)与转折(2022-06 十二个月窗转正)。 |
| 结论是否超出证据 | 通过 | 结论为否定性主张(「可外推某一段事后路径」不成立)并写明「只作结构对照与情景校准,不作预测」「相似≠因果≠预测」,强度低于证据所允许。 |
| 证伪条件可观测性 | 通过(注明) | 本条为否定性主张,不需要触发阈值;情景面另给可观测阈值(3.3)。 |

### 2.3 C3 中国政策与美欧日方向的背离

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过(注明) | 四项引用 CN_PPI_YOY@2026-10-31、CN_CPI_YOY@2026-10-31、CN_LPR_1Y@2026-11-20、USDCNY@2026-11-23 均在证据索引内;前两项按「标签日=观测月末、序列观测日=月初」解析到 2026-10-01 的 5.7 与 0.7。USDCNY 被引用而正文未用(MINOR-6)。 |
| 支持度 | 通过 | CN_PPI_YOY 自深负值区间(如 2025-06 的 −3.6)升至 2026-10 的 5.7;「四大经济体最大价格摆动」=12 个月变动 +7.80 个百分点,其余(美国 CPI、欧元区 HICP、日本 CPI、中国 CPI)最大 +1.90;CN_LPR_1Y 三锚均 3.0、末观测 2026-11-20;CN_OMO_7D 末观测 2026-10-30 的 1.4;新锚 CN_POLICY_OVERNIGHT 自 2026-11-02 起 16 个观测全为 1.25。 |
| 竞争解释 | 通过 | A(输入型/供给驱动,看 PPI–CPI 剪刀差 5.0 个百分点)、B(内需制约,看 PMI 与信贷)、C(汇率/资本流动)预期方向不同。 |
| 反对证据 | 通过(注明) | CN_NEW_LOANS 月度值正负交替(2026-04 −4006、2026-07 −5896、2026-10 −5846),不能稳定支持 B;陈述如实写「不足以在三种解释间裁决」。 |
| 结论是否超出证据 | 通过 | 三种解释并列,整条标【尚未验证】,未指定赢家。 |
| 证伪条件可观测性 | 通过(注明) | A/B 的区分指标在库(PPI、CPI、PMI、新增贷款);C 的资本流动序列不在库,陈述如实标「当前不可检验」而非给出无法观测的阈值。 |

### 2.4 M1 主链(通胀再加速→政策再收紧→实际利率上行→风险资产承压)

**M1-1 冲击环【事实/E1】**

- 证据相关性: 通过 — 引用 CPI@2026-10-01、CORE_PCE@2026-09-01、EA_HICP_YOY@2026-10-01、CN_PPI_YOY@2026-10-31 四项均在证据索引内。
- 支持度: 通过 — CPI 同比 2.434→4.1666(2026-02→2026-05;基期 2025-02 与 2025-05 指数在库)、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY −0.9→3.9;CORE_PCE 同比 2026-05 高点 3.16→2026-07 3.00→2026-09 3.12,未越过 3.1617;EA_HICP_YOY 2026-06 回落至 2.8 后升至 4.0@2026-10;CN_PPI_YOY 2026-07 回落至 3.5 后升至 5.7@2026-10。
- 竞争解释: 通过 — 传导面同环给出「需求过热或基数效应」竞争解释与区分指标 BRENT_F(对质结果见 3.1)。
- 反对证据: 通过(注明) — 布伦特月末口径 2026-02-27 72.48→2026-03-31 118.35→2026-05-29 92.05: 首尾 +27.00%(合「同窗显著上行」),但 3 月末冲高后至 5 月末回落,至 2026-06 月末 72.92 才回到首月末水平;判断档写「未持平」,其「回落至首月末附近」一语与同行「首尾 +27.00%」措辞相抵(已记入 MINOR-1)。
- 结论是否超出证据: 通过 — 本环只陈述同窗回升事实;「供给/能源冲击推升」在传导面标【假设】、E3。
- 证伪条件可观测性: 通过(注明) — 事实环无阈值;区分指标 BRENT_F 在库(末观测 2026-11-23)。

**M1-2 政策环【时序为事实,动机为假设/E3】**

- 证据相关性: 部分通过(MINOR-2) — 「因通胀续升而收紧」的动机论证只用美国 CPI。欧央行 2026-09-10 决议前可见的本地区通胀(EA_HICP_YOY 2026-08 观测 3.2,高于 2026-07 的 2.9)与日本央行 2026-09-18 决议前可见的日本 CPI(2026-07 观测 1.97,高于 2026-04 的 1.38)均处回升段,「动机环证据减弱」只对美联储成立。
- 支持度: 通过 — 时序: 通胀转折窗至 2026-05,政策变动月自 2026-06 起。生效日=序列值变更日: 欧央行 2026-06-17(ECB_MRO 2.15→2.4、ECB_DFR 2.0→2.25)与 2026-09-16(2.4→2.65、2.25→2.5);美联储 2025-12-11(DFEDTARU 4.0→3.75,DFF 3.89→3.64)与 2026-09-17(3.75→4.0,DFF 3.63→3.88)。决议日: 日本央行 2026-09-18(冻结日历实录);美联储 2026-09-16、欧央行 2026-06-11 与 2026-09-10 为引擎按惯例自生效日回推,席位按同一惯例独立回推所得相同,判断档已标【推断】。决议前可见的美国 CPI 同比: 欧央行 2026-06-11 前 2026-04 观测 3.78;2026-09-10 前 2026-07 观测 3.30;美联储 2026-09-16 与日本央行 2026-09-18 前 2026-08 观测 3.35;决议后发布的 2026-09 观测 3.72——均与 series_store 按席位可见性规则推出的值一致(冻结日历对 2026 年各观测月无 CPI、HICP、日本 CPI 条目,按 0.3 节约定规则推定;逐值见 info_decision_cpi.txt,由 s42_decision_cpi.py 自快照计算)。
- 竞争解释: 通过 — 传导面给出「收紧另有动机(金融稳定/汇率/正常化独立进程)」,区分指标 BEI_10Y;日本自 2025-12 起上调早于美欧通胀窗,被如实写为对单一叙事的反例。
- 反对证据: 通过(注明) — 决议前可见的美国 CPI 已自高点回落;环内正文主动披露并据此下调动机环证据。
- 结论是否超出证据: 通过 — 明写「不可由本引擎数据验证,整环为【假设】」。
- 证伪条件可观测性: 通过 — 证伪指标 CPI,阈值「回落至 2.5 以下而央行仍续紧」;CPI 同比近 24 个月有 6 个月低于 2.5(最近 2026-02 的 2.434),阈值可达。

**M1-3 利率环【事实/E1】**

- 证据相关性: 通过 — 引用 UST_10Y@2026-11-19、TIPS_10Y@2026-11-19、BEI_10Y@2026-11-20。
- 支持度: 通过 — 2025-11-19→2026-11-19: 4.13→5.04(+91bp)=1.86→2.88(+102bp)+2.27→2.16(−11bp),残差 0;最新 BEI_10Y 2.15@2026-11-20。
- 竞争解释 / 反对证据 / 结论 / 证伪: 本环为恒等分解事实,无解释分支与阈值需求;通过(注明)——BEI_10Y 回落本身与「通胀再加速→市场为持续通胀定价」的直觉相反,环内如实写「市场通胀预期(盈亏平衡)反而回落」。

**M1-4 资产环【E2,缺环为假设】**

- 证据相关性: 通过 — 引用 SPX、NIKKEI225、GOLD_F、DXY、VIX、TIPS_10Y、HY_OAS 七项,均在证据索引内,观测日 2026-11-23/20/19 与文字的口径说明一致。
- 支持度: 通过 — SPX −5.51%、NIKKEI225 −9.98%、GOLD_F −8.05%、DXY +2.23%、VIX 19.45→27.01(2026-10-23→2026-11-23,NIKKEI225 止于 2026-11-20);收盘口径 SPX −9.36%、VIX +84.52%(至 2026-11-20);HY_OAS 3.52@2026-11-19、序列高点 4.61@2025-04-07、第 91.98 百分位。
- 竞争解释: 通过 — 传导面同环给出「增长担忧主导」,区分指标 BEI_10Y(辅 TIPS_10Y、HY_OAS)。
- 反对证据: 通过(注明) — 利率腿取 12 个月窗、资产腿取近 1 个月窗,两腿不同窗(MINOR-3);12 个月窗 SPX +8.03%、NIKKEI225 +22.47% 与「实际利率上行压制风险资产」相左。
- 结论是否超出证据: 通过 — 明写「只有共动事实(相关≠因果)…此环为【假设】」。
- 证伪条件可观测性: 通过 — HY_OAS 升破 4.61(序列高点,2025-04-07),数字阈值、指标在库(末观测 2026-11-19)。

### 2.5 M2 竞争链(日本持续正常化→全球期限溢价/套息渠道)

**M2-1【事实/E1】**

- 证据相关性: 通过 — 引用 JP_POLICY_RATE@2026-10-01、USDJPY@2026-11-23。
- 支持度: 通过 — 月均 0.478@2025-11→1.227@2026-10,净 +74.9 个基点(报告写 +75bp);月度步进 2025-12 +8、2026-01 +17、2026-06 +11、2026-07 +14、2026-09 +7、2026-10 +18 个基点(直算 7.9/17.1/11.4/13.7/6.6/18.4),2026-04 与 2026-08 各为 −0.1 个基点的舍入变动;「自 2025-12 的 0.557 起为 +67bp」与引擎面板 +67bp 一致。
- 竞争解释: 通过 — 传导面 TR2 给出「美国国内定价主导」竞争解释,区分指标 USDJPY。
- 反对证据: 通过 — 同窗 SPX −5.51% 而 USDJPY 156.49→159.35(+1.82%),主解释预期未获支持,传导面如实写「分量应被下调」。
- 结论是否超出证据: 通过 — 只陈述「唯一在通胀共振前已开始上调、窗内未回撤」: 美联储先降(2025-12-11)后升(2026-09-17)、欧央行自 2026-06 起、中国持平,对比成立。
- 证伪条件可观测性: 通过 — 见 M2-2。

**M2-2【E3,整环假设】**

- 证据相关性: 通过(注明) — 明写「本引擎无 JGB 历史序列(单点观测)」: series_store 92 条序列名中无 JGB;facts 仅有 JGB2Y 1.853、JGB5Y 2.235、JGB10Y 2.87@2026-11-19 三个单点,无法构成序列。
- 支持度: 不适用(整环自标不可验证)——环内没有借单点值支撑因果,不构成问题。
- 竞争解释 / 反对证据: 通过 — 同 M2-1。
- 结论是否超出证据: 通过 — 「整环不可验证,为【假设】」。
- 证伪条件可观测性: 通过 — USDJPY 在库(末观测 2026-11-23);条件「风险资产再次收缩而 USDJPY 未同步走低/日元未走强」可观测。同窗该条件已被满足一次,判断档据此下调分量而未直接宣告证伪,属保守处理(见 3.1 第 4 环)。

### 2.6 证据级标注相称性

标注分布: M1-1 E1、M1-2 E3、M1-3 E1、M1-4 E2、M2-1 E1、M2-2 E3。核对: (a) 标 E1 的三环内容均为序列可直接复算的事实(同窗回升、三利率恒等分解、政策利率月均路径),复算全部命中;(b) 标 E2 的资产环明示「可验证环=共动事实,缺失环=因果传导为假设」,未把共动写成因果;(c) 标 E3 的两环(动机、JGB 溢出)均明写【假设】或不可验证,且各给出可观测的证伪指标。未见「事实标成假设」或「假设标成事实」的错配。情景面两情景的置信档均为『有历史相似证据』,并同时写出事后路径的分歧与样本非独立,相称。

## 3. 专项核对: 对质面、历史段同步性、情景与证伪

### 3.1 对质面(传导面四环)

判断档 quality_gate_notes[1] 称「4 环均给出主/竞争两侧对同一区分指标的不同预期，判断=尚不能区分 ×4」。逐环核对:

| 环 | 区分指标 | 主解释预期 | 竞争解释预期 | 库内同窗观测(席位直算) | 「尚不能区分」与观测是否相符 |
|---|---|---|---|---|---|
| TR1 第1环(冲击环) | BRENT_F | 供给冲击主导→BRENT_F 在 2026-02 至 2026-05 同窗显著上行 | 需求/基数主导→BRENT_F 同窗大体持平而 CORE_CPI 上行 | 月末口径 2026-02-27 72.48→2026-03-31 118.35→2026-05-29 92.05,首尾 +27.00%;CORE_CPI 同比 2.47@2026-02→2.82@2026-05 | 偏保守: 主解释预注册的「显著上行」成立,竞争解释预注册的「大体持平」未获支持;CORE_CPI 同窗上行对两解释均相容,不是区分观测(MINOR-1) |
| TR1 第2环(政策环) | BEI_10Y | 通胀动机主导→BEI_10Y 在政策收紧前处上行段且高位 | 非通胀动机主导→BEI_10Y 与政策节奏脱钩(政策续紧而 BEI_10Y 不升) | 2026-02-27 2.25→2026-05-04 2.50(合主);2026-06-10 2.34;2026-06-17 起区间 2.15–2.40;近 28 个日历日 2026-10-23 2.34→2026-11-20 2.15(合竞) | 相符: 窗内方向前后相反 |
| TR1 第3环(利率环→资产环) | BEI_10Y(辅 TIPS_10Y、HY_OAS) | 利率主导→TIPS_10Y 续升而 BEI_10Y 稳定、HY_OAS 不升破序列高点 | 增长主导→BEI_10Y 明显下行且 TIPS_10Y 转平/回落、HY_OAS 走阔 | 共同交易日 2026-10-20→2026-11-19: TIPS_10Y 2.77→2.88(+11bp,合主)、BEI_10Y 2.35→2.16(−19bp,合竞);HY_OAS 3.52@2026-11-19,低于 4.61,近 1 周走阔 0.29 个百分点而未破前高 | 相符: TIPS 一侧合主、BEI 一侧合竞,交叉;HY_OAS 两侧各有相容观测 |
| TR2 第4环(日本环→全球溢出) | USDJPY | 日本正常化溢出主导→风险资产收缩窗口与日元走强(USDJPY 走低)同现 | 美国国内定价主导→USDJPY 走势与风险资产收缩在时间上解耦 | 同窗 2026-10-23→2026-11-23 SPX −5.51% 而 USDJPY 156.494→159.347(+1.82%),主解释预期未获支持;逐日面(库内可得、未入档): 21 个交易日 SPX 与 USDJPY 日变动相关系数 0.191,SPX 下跌的 12 日中 9 日 USDJPY 下跌,但幅度可忽略 | 偏保守: 判断档已写「分量应被下调」,却仍记「尚不能区分」(MINOR-1);逐日面未入档(NIT-1) |

附注(记入 MINOR-1): 对质表「已有观测」列四行均为引擎近 30 日面(如第 1 环 BRENT_F 116.72→88.19,−24.44%),与各行的预注册窗(如第 1 环的 2026-02 至 2026-05)不对应。

结论: 第 2、3 环与观测相符;第 1、4 环判「尚不能区分」偏保守,但判断档正文已写明哪一侧未获支持,属少判而非夸大——记 MINOR-1,不构成 REVISE。

### 3.2 历史段同步性

判断档三段的「其他经济体是否同步」取引擎同步面的通胀维方向(相对美国),句内写明口径「引擎同步面(通胀维方向,相对美国)」与「截至…已发布数据」。核对:

- (a) 通胀维标签 9/9 与引擎面一致: 2025-03 中国分化、欧元区分化、日本同步;2022-06 三地同步;2023-10 三地分化。
- (b) 所引当时可知值逐一命中且在各自截止日前可见: 2025-02 欧元区 HICP 2.3、日本 CPI 3.66、中国 PPI −2.2、中国 CPI −0.7;2022-05 为 8.1/2.46/6.4/2.1;2023-10 欧元区 HICP 2.9(月末快报)、2023-09 日本 CPI 3.05、中国 PPI −2.5、中国 CPI 0.0。
- (c) 全维引擎表(增长/通胀/政策)九格中「同步」格数: 2025-03 为 3、2022-06 为 5、2023-10 为 1(底层读数变化 36 行为信息行)。引导词『部分同步 / 同步 / 不同步』与全维表不冲突,但引导词语义只由通胀维支撑,增长与政策维未进入叙述(MINOR-4)。
- (d) 叙述与面无冲突、无缺证: 三段标签在引擎面均在场。

结论: 不构成规程第 4 节意义上的「叙述与面冲突」或「称同步而面=缺证」。

### 3.3 情景与证伪阈值

| 情景 | 触发条件(判断档原文要点) | 截止日读数(席位直算) | 触发状态 | 证伪阈值 | 阈值可观测性 | 证伪状态 |
|---|---|---|---|---|---|---|
| SCN1 基准情景(假设非预测) | 美国 2026-11 或 2026-12 月 CPI 同比继续 ≥3.5,或欧央行/美联储再加息 | CPI 同比 3.72@2026-09(2026-10 同比缺基期不可得);ECB_DFR 末观测 2.5@2026-09-16、DFEDTARU 4.0@2026-11-23,冻结日历无其后新决议实录 | 未触发(2026-11 CPI 未发布;未见新加息) | CPI 同比<2.5 且 CORE_PCE<2.8 持续两个月 | CPI<2.5 在近 24 个月中有 6 个月成立(最近 2026-02 的 2.434);CORE_PCE<2.8 有 5 个月(最近 2025-11 的 2.721);截止日读数 3.72 与 3.12 | 未证伪 |
| SCN2 反例情景(假设非预测) | 欧央行或美联储下一次决议为降息或明确暂停指引,或美国 CPI 同比自 2026-11 观测月起连续两个月回落 | 下一次决议在截止日之后 | 未触发(待观测) | BEI_10Y 跌破 1.8 且继续下行 | BEI_10Y 2.15@2026-11-20;库内最近一次低于 1.8 为 2020-11-30(1.77),近 24 个观测 0 次触及——可观测但偏宽(NIT-11) | 未证伪 |

- 两情景方向互补: SCN1(通胀延续、维持收紧)→股指倾向承压或高波动、GOLD_F 受压、DXY 偏强、VIX 中枢抬升;SCN2(通胀一次性、转向宽松)→股指修复、GOLD_F 修复走强、DXY 转弱。SPX、GOLD_F、DXY 三个指标在两情景下的方向逐一相反;期限均为 2027-02-28。
- SCN1 触发条件中「决议日见发布日历实录」与冻结日历不符(日历无美联储、欧央行条目),记 MINOR-5。
- 所引相似段事后值(2022-06 三个月窗 SPX −5.28%、GOLD_F −7.49%、DXY +7.10%;2025-03 十二个月窗 GOLD_F +48.83%、DXY −4.08%、SPX +16.33%)与台账 history 行一致;贡献 42.1%+40.7% 与引擎面 42.1281/40.66 一致。

## 4. 反方攻击记录

对每条 L3 矛盾陈述、每条机制链至少做一次反方攻击,共 29 次;逐次内容与结果如下(内容与 VERDICT-round1.json 的 counterexamples_sought 一致,每条在问句后的箭头处拆成「攻击问句」与「结果」两栏)。没有一次攻击得到「数字/日期/方向错」或「结论超出证据且无标注」的结果;得到「部分成立」的攻击已分别落到第 6 节的 MINOR/NIT 条目。

| 序号与对象 | 攻击问句 | 结果 |
|---|---|---|
| 反方攻击 1 (C1) | 『DFF 回到降息前水平』是否以目标区间上限冒充有效利率? | 否: DFF 3.88→3.63→3.88(2025-11-22/2026-08-22/2026-11-19)与 DFEDTARU 4.0→3.75→4.0 两口径分列,各自与 series_store 一致。 |
| 反方攻击 2 (C1) | 『CPI 与 CORE_PCE 同比较一年前走高』是否含缺基期的同比? | 否: CPI 2026-10 同比如实标『缺 2025-10 基期不可得』,比较用 2026-09 观测 3.72 对 2025-09 观测 3.02;CORE_PCE 3.12@2026-09 对 2.85@2025-08,基期均在库。 |
| 反方攻击 3 (C1) | 『CN_PPI_YOY 续创本轮新高』『EA_HICP_YOY 升至本轮最高』是否成立? | 成立: CN_PPI_YOY 2025-11..2026-10 最大值 5.7@2026-10,且 2026-07..10 逐月 3.5/3.8/5.0/5.7;EA_HICP_YOY 最大值 4.0@2026-10。 |
| 反方攻击 4 (C1) | 三种解释是否稻草人? | 否: A/B/C 对 BEI_10Y、TIPS_10Y、HY_OAS、USDJPY 的预期方向互异;近 1 个月 TIPS_10Y +11bp(合A)与 BEI_10Y −19bp(合B)并存。 |
| 反方攻击 5 (C1/M1) | 12 个月窗内『实际利率上行→风险资产收缩』是否成立? | 不成立: SPX +8.03%、NIKKEI225 +22.47% 与 TIPS_10Y +102bp 同向上行(共同交易日 2025-11-19→2026-11-19);陈述已限定『近月收缩』,未披露该反向事实(记 MINOR)。 |
| 反方攻击 6 (C2) | 历史事后段是否被写成预测或越出截止日? | 否: 三段 3/6/12 月共 99 个数值按自然月末口径复算一致,均标『事后/非预测』;『当时可知』值逐项核验在锚日前可见。 |
| 反方攻击 7 (C2) | 符号一致率与类比距离是否与引擎面一致? | 一致: 1/3/6/12 个月窗 SPX 0.6/0.6/1.0/1.0、UST_10Y 0.8/0.6/0.8/0.6、DXY 0.6/0.6/0.8/0.8、GOLD_F 0.6/0.8/1.0/1.0;距离 0.7272/0.7918/1.0542、分位 0.0/1.37/30.14。 |
| 反方攻击 8 (C3) | 『不足以在三种解释间裁决』是否忽视了库内可裁决证据? | 否: CN_NEW_LOANS 月度正负交替(2026-04 −4006、2026-07 −5896、2026-10 −5846),同比无法稳定判读;USDCNY(12 个月 −6.19%)只触及解释C的汇率腿(记 MINOR),不能裁 A/B。 |
| 反方攻击 9 (C3) | 『LPR 与 7 天逆回购窗内持平』是否把缺席写成无变化? | 否: CN_LPR_1Y 三锚 3.0 且末观测 2026-11-20;CN_OMO_7D 末观测 2026-10-30 的 1.4(滞后 24 天,已披露过期);新锚 16 个观测全为 1.25(自 2026-11-02)。 |
| 反方攻击 10 (C3) | 『四大经济体最大价格摆动』是否成立? | 成立: CN_PPI_YOY 12 个月变动 +7.80 个百分点,其余(CPI/EA/JP/CN CPI)最大 +1.90。 |
| 反方攻击 11 (M1) | 冲击环同比是否基期错配? | 否: CPI 2026-02 2.434、2026-05 4.1666(基期 2025-02 319.679、2025-05 320.620 在库);EA_HICP_YOY 1.9→3.2;CN_PPI_YOY −0.9→3.9。 |
| 反方攻击 12 (M1) | 2025-12 美联储是降息,『政策再收紧』是否失实? | 否: 正文写明 2025-12-11 生效 −25bp、2026-09-17 生效 +25bp『回补此前降息』,窗内净 0;欧央行两次各 +25bp、日本 +67bp(自窗内首观测)。 |
| 反方攻击 13 (M1) | 动机环以美国 CPI 论证欧/日决议,证据是否相关? | 部分不相关: 两地决议前可见的本地区通胀在回升段(HICP 2026-08 观测 3.2;日本CPI 2026-07 观测 1.97),『证据减弱』只对美联储成立(记 MINOR)。 |
| 反方攻击 14 (M1) | 三利率恒等式是否成立? | 成立: 2025-11-19→2026-11-19 UST_10Y 4.13→5.04(+91bp)=TIPS_10Y 1.86→2.88(+102bp)+BEI_10Y 2.27→2.16(−11bp)。 |
| 反方攻击 15 (M1) | 资产环盘中/收盘口径与 HY_OAS 数字是否属实? | 属实: SPX 2026-10-23→2026-11-20 −9.36%、VIX +84.52%;HY_OAS 3.52 处序列第 91.98 百分位、为 2025-05-09 以来最高,严格 7 日 +0.32pp、12 个月 +0.35pp。 |
| 反方攻击 16 (M2) | 『四地中唯一在通胀共振前已开始上调、窗内未回撤』是否成立? | 成立: JP_POLICY_RATE 自 2025-12 起 +8/+17/+11/+14/+7/+18 至 1.227;美联储先降后升、欧央行自 2026-06 起、中国持平。 |
| 反方攻击 17 (M2/TR2) | 套息渠道在近月窗口是否有支持? | 同窗无: SPX −5.51% 而 USDJPY +1.82%;逐日面方向计数弱支持(12 个下跌日中 9 日日元走强)但幅度可忽略,『尚不能区分』可站住。 |
| 反方攻击 18 (M2) | JGB 序列缺席是否属实? | 属实: series_store 92 条序列名中无 JGB。 |
| 反方攻击 19 (情景) | 截止日读数是否已触发或已证伪情景? | 均未: CPI 同比 3.72@2026-09、CORE_PCE 3.12@2026-09、BEI_10Y 2.15@2026-11-20,未触及 CPI 2.5/CORE_PCE 2.8/BEI_10Y 1.8 阈值;两情景方向互补。 |
| 反方攻击 20 (截止纪律) | 是否有晚于 2026-11-23 的观测、发布或生效被引用? | 无: 全部引用观测日不晚于 2026-11-23(盘中值已标注);research_as_of 2026-11-23T22:53:47+08:00 下纽约 09:53、法兰克福 15:53 常规时段进行中,东京已收盘(末值 2026-11-20),与说明相容。 |
| 反方攻击 21 (同步面) | 三段同步性叙述是否与引擎面冲突或缺证? | 无冲突: 通胀维 9/9 标签一致;引导词未覆盖增长/政策维(2022-06 全维九格中五格同步),引擎全维表紧随其后(记 MINOR)。 |
| 反方攻击 22 (转折) | 『谁先变』是否有时间分辨率支撑? | 有: 正文一律写『月频分辨率下先后未定』,并说明日本下行段属窗口边缘效应;美欧低点同为 2026-01、中国 PPI 窗内低点 2025-11。 |
| 反方攻击 23 (Gate A) | 披露是否属实? | 属实: status=DEGRADED,核心缺口 0、非核心缺口 7、非核心降级 8,清单与快照逐项一致;五项存量观测被引用一事已披露。 |
| 反方攻击 24 (对质表) | 『尚不能区分』是否与各行观测一致? | 第2、3环一致;第1环与第4环偏保守(MINOR)。 |
| 反方攻击 25 (候选面) | 引擎转折候选面的窗口、前值、后值与 Δ 是否与冻结快照一致? | 窗口 9/9、前值 9/9、后值 9/9 与按引擎规则(相隔三个观测的最大变化)的席位重算一致;Δ 8/9 逐位一致;CORE_CPI 行 Δ 面值 -0.3767 为端点舍入后相减,未舍入直算 -0.3768(末位,记 MINOR);行序按 \|Δ\| 降序成立。 |
| 反方攻击 26 (引用) | 判断档 L3/L4 的 50 处证据引用是否都在本轮证据索引与冻结快照内、且不晚于截止日? | 是: 20 个不同引用全部在证据索引(72 行)内,18 个按日期精确命中序列库;CN_PPI_YOY@2026-10-31 与 CN_CPI_YOY@2026-10-31 两个引用按『标签日=观测月末、序列观测日=月初』双标签命中(值 5.7/0.7),该双标签已由判断档披露;全部观测日不晚于 2026-11-23。 |
| 反方攻击 27 (情景) | 证伪阈值是否可观测、是否已被截止日读数跨越? | 可观测: CPI 同比<2.5 在近 24 个月中有 6 个月成立(最近 2026-02 的 2.434)、CORE_PCE<2.8 有 5 个月(最近 2025-11 的 2.721)、HY_OAS 4.61=序列高点(2025-04-07);BEI_10Y<1.8 库内最近一次为 2020-11-30(1.77),阈值偏宽、取值依据未说明(记 NIT);截止日读数均未跨越任何阈值。 |
| 反方攻击 28 (政策面) | 决议日、生效日、官方目标值与距上次调整天数是否有实录或序列依据? | 有: 日本央行三项来自冻结日历实录(决议 2026-09-18、生效 2026-09-24、目标 1.25;2026-10-30 确认维持);美联储与欧央行的生效日=序列值变更日(2025-12-11、2026-09-17;2026-06-17、2026-09-16),决议日为引擎按惯例自生效日回推(2025-12-10、2026-09-16;2026-06-11、2026-09-10),判断档已标【推断】并写明日历无实录;距上次调整(按生效日)60 天、距决议 66 天、距维持 24 天直算一致;无待生效决定。 |
| 反方攻击 29 (C2) | 『2025-03、2023-10 段风险资产与 GOLD_F 多数窗走强而 DXY 走弱』『2022-06 段三个月窗股指均为负、十二个月窗除上证外转正』的方向归纳是否与逐窗值一致? | 一致: 2025-03 段 15 窗全正、2023-10 段 14/15(上证三个月窗 -7.63),DXY 两段各 3/3 窗为负;2022-06 段三个月窗 SPX -5.28、NIKKEI225 -1.73、DAX -5.24、SHCOMP -11.01,十二个月窗 SPX +17.57、NIKKEI225 +25.75、DAX +26.32、SHCOMP -5.78。 |

## 5. 规程第 3 节覆盖核对

### 5.1 逐项

| 项 | 规程要求 | 本席所做 | 结果 |
|---|---|---|---|
| ① | 截止日与截止纪律 | 全部 20 个证据引用解析到的观测日 ≤2026-11-23;research_as_of=2026-11-23T22:53:47+08:00 换算为纽约 09:53、法兰克福 15:53、东京 23:53、上海 22:53;止于 2026-11-23 的 SPX、DAX、CAC40、VIX、GOLD_F、DXY、BRENT_F、USDJPY 标「盘中快照」,NIKKEI225 止于 2026-11-20,SHCOMP 为 2026-11-23 收盘——与各市场常规时段相容;另一口径(收盘 2026-10-23→2026-11-20: SPX −9.36%、DAX −1.50%、CAC40 +1.86%、NIKKEI225 −9.98%、VIX +84.52%)复算命中 | 通过 |
| ② | 点值锚格 | 22 格×3 锚=66 格: 63 格取值与观测月命中,3 格为引擎标 no_published_observation_on_or_before_anchor 的诚实缺席(CN_POLICY_OVERNIGHT 的 12 个月前与 3 个月前、JP_CPI_TOKYO_YOY 的 12 个月前);同比派生值逐格对引擎格 | 通过(台账 anchors 275 行) |
| ③ | 同比 | CPI 2026-10 同比因 2025-10 观测缺席不可得,判断档如实标明,比较改用 2026-09 对 2025-09(3.72 对 3.02);CORE_PCE 10 月同比同理未给出;水平序列同比均以同月一年前为基期 | 通过 |
| ④ | 政策面 | 日本央行决议日 2026-09-18、生效日 2026-09-24、目标 1.25、2026-10-30 确认维持均取自冻结日历实录;美联储与欧央行生效日=序列值变更日,决议日为惯例回推(判断档标【推断】);JP_POLICY_TARGET 不在注册表,JP_POLICY_RATE 明示为月均口径,不以月均冒充官方目标;DFF(有效利率)与 DFEDTARU(目标区间上限)分列,LPR 作为报价基准分列;距上次调整(按生效日)60 天、距决议 66 天、距维持 24 天与读者报告引擎政策官方记录面一致,美联储/欧央行生效日距研究截止 67/68 天一致;无待生效决定 | 通过(台账 misc 政策面 32 行;天数由引擎面给出,判断档未写天数) |
| ⑤ | 三利率分解与资产月窗 | 12 个月窗(2025-11-19→2026-11-19)名义 +91bp=实际 +102bp+盈亏平衡 −11bp,残差 0;近 1 个月共同交易日(2026-10-20→2026-11-19)−8/+11/−19,残差 0;资产月窗 2026-10-23→2026-11-23: SPX −5.51%、SHCOMP −4.11%、DAX +0.11%、NIKKEI225 −9.98%、VIX +38.87%、DXY +2.23%、GOLD_F −8.05%;盘中与收盘两口径、各序列终止日均与 series_store 一致 | 通过(两腿不同窗记 MINOR-3) |
| ⑥ | 转折判断、候选面与「先后」 | 三转折与补选的数值(CPI 2.434→4.1666、INDPRO 1.7543→0.7972、JP_CPI_YOY 2.9→1.27、东京 CPI 1.6→2.69)与「月频分辨率下先后未定」「日本下行段属窗口边缘效应」的时间分辨率说明均核验;候选面 9 项窗口 9/9、前值 9/9、后值 9/9 与按引擎规则(相隔三个观测的最大变化)的席位重算一致,Δ 8/9(唯一偏离=CORE_CPI 行末位舍入,MINOR-9);行序按 Δ 绝对值降序成立;「候选面最大美欧值」=CPI 的 Δ 绝对值 1.7326 成立 | 通过(注明) |
| ⑦ | 传导链各环 E1/E2/E3 标注相称 | 见 2.6 | 通过 |
| ⑧ | 历史类比: 当时可知面与事后段 | 三段「当时可知」值 12 项与可见月份逐一核验;事后 3/6/12 月 99 值按月末口径复算一致,措辞均为「事后/事后结果≠预测」;C2 陈述的方向归纳 4 行核对成立;引擎事后块 48 值与 report.json 一致;两口径起点不同(引擎=锚后首个观测,判断档=自然月末)已在判断档说明 | 通过 |
| ⑨ | 情景触发条件、证伪阈值、期限、相容与互补 | 见 3.3 | 通过(MINOR-5、NIT-11) |
| ⑩ | 总判断与走位文字数值一致性;对质表「尚不能区分」 | 头条结论与走位文字中的数值全部命中;对质表四环中两环与观测相符、两环偏保守(MINOR-1);对质表的主/竞争预期与传导面正文一致 | 通过(注明) |
| ⑪ | 诚实缺席项与 Gate A | Gate A status=DEGRADED,核心缺口 0、非核心缺口 7、非核心降级 8,清单与快照逐项一致;五项存量观测(CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)被引用并披露过期/降级;CPI 2026-10 同比缺基期、JP_POLICY_TARGET 不在册、JGB 仅单点、中国利率预期序列不在库,均如实披露 | 通过 |
| ⑫ | 截止日当日日频观测时点口径与 research_as_of 相容 | 见 ① | 通过 |
| ⑬ | 契约验证非 VERIFIED 项披露一致 | 契约验证 14 项全部 VERIFIED(覆盖 C1 陈述 11 项与 C3 陈述 3 项),six_checks 16/16、map_checks 7/7,unresolved_unbound 为空;无非 VERIFIED 项需要披露。C2 陈述的历史事后数字不在契约绑定范围,已由本席另行复算(99 值全中) | 通过 |
| ⑭ | 交付门缺口披露 | 未把缺席写成「无变化」: 中国「窗内无变动」限于有观测的 LPR 与 7 天逆回购,并披露新锚无法核验全年、换锚后原工具无新观测;未把序列值写成官方宣布目标: JP_POLICY_RATE 明示为月均,官方目标 1.25 单独取自日历实录 | 通过 |

### 5.2 三时点对照表(由台账 anchors 行生成;「观测月: 直算」=席位按 0.3 节可见性规则推出的最新可见观测月)

| 地区 | 维度 | 指标 | 锚 | 值: 报告 | 值: 直算 | 观测月: 报告 | 观测月: 直算 | 引擎格值 | 引擎格观测月 | 同比: 直算 | 同比: 引擎格 | 一致与否 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 美国 | 增长 | US_REAL_GDP | 12个月前 | 23884.563 | 23884.563 | 2025-04 | 2025-04 | 23884.563 | 2025-04 | 2.4206 | 2.42 | 一致 |
| 美国 | 增长 | US_REAL_GDP | 3个月前 | 24408.011 | 24408.011 | 2026-04 | 2026-04 | 24408.011 | 2026-04 | 2.1916 | 2.19 | 一致 |
| 美国 | 增长 | US_REAL_GDP | 最新一期 | 24611.077 | 24611.077 | 2026-07 | 2026-07 | 24611.077 | 2026-07 | 2.0657 | 2.07 | 一致 |
| 美国 | 增长 | UNEMPLOYMENT | 12个月前 | 4.4 | 4.4 | 2025-09 | 2025-09 | 4.4 | 2025-09 | — | — | 一致 |
| 美国 | 增长 | UNEMPLOYMENT | 3个月前 | 4.1 | 4.1 | 2026-07 | 2026-07 | 4.1 | 2026-07 | — | — | 一致 |
| 美国 | 增长 | UNEMPLOYMENT | 最新一期 | 4.1 | 4.1 | 2026-10 | 2026-10 | 4.1 | 2026-10 | — | — | 一致 |
| 美国 | 增长 | INDPRO | 12个月前 | 101.6247 | 101.6247 | 2025-08 | 2025-08 | 101.6247 | 2025-08 | 1.1887 | 1.19 | 一致 |
| 美国 | 增长 | INDPRO | 3个月前 | 103.1675 | 103.1675 | 2026-07 | 2026-07 | 103.1675 | 2026-07 | 1.2498 | 1.25 | 一致 |
| 美国 | 增长 | INDPRO | 最新一期 | 103.3954 | 103.3954 | 2026-10 | 2026-10 | 103.3954 | 2026-10 | 2.1497 | 2.15 | 一致 |
| 美国 | 通胀 | CPI | 12个月前 | 324.245 | 324.245 | 2025-09 | 2025-09 | 324.245 | 2025-09 | 3.0226 | 3.02 | 一致 |
| 美国 | 通胀 | CPI | 3个月前 | 332.813 | 332.813 | 2026-07 | 2026-07 | 332.813 | 2026-07 | 3.3039 | 3.3 | 一致 |
| 美国 | 通胀 | CPI | 最新一期 | 337.476 | 337.476 | 2026-10 | 2026-10 | 337.476 | 2026-10 | 不可得(null) | 不可得(null) | 一致 |
| 美国 | 通胀 | CORE_CPI | 12个月前 | 330.418 | 330.418 | 2025-09 | 2025-09 | 330.418 | 2025-09 | 3.02 | 3.02 | 一致 |
| 美国 | 通胀 | CORE_CPI | 3个月前 | 336.789 | 336.789 | 2026-07 | 2026-07 | 336.789 | 2026-07 | 2.4665 | 2.47 | 一致 |
| 美国 | 通胀 | CORE_CPI | 最新一期 | 339.9 | 339.9 | 2026-10 | 2026-10 | 339.9 | 2026-10 | 不可得(null) | 不可得(null) | 一致 |
| 美国 | 通胀 | CORE_PCE | 12个月前 | 126.646 | 126.646 | 2025-08 | 2025-08 | 126.646 | 2025-08 | 2.8513 | 2.85 | 一致 |
| 美国 | 通胀 | CORE_PCE | 3个月前 | 129.969 | 129.969 | 2026-06 | 2026-06 | 129.969 | 2026-06 | 3.0412 | 3.04 | 一致 |
| 美国 | 通胀 | CORE_PCE | 最新一期 | 130.902 | 130.902 | 2026-09 | 2026-09 | 130.902 | 2026-09 | 3.1212 | 3.12 | 一致 |
| 美国 | 政策 | DFEDTARU | 12个月前 | 4.0 | 4.0 | 2025-11 | 2025-11 | 4.0 | 2025-11 | — | — | 一致 |
| 美国 | 政策 | DFEDTARU | 3个月前 | 3.75 | 3.75 | 2026-08 | 2026-08 | 3.75 | 2026-08 | — | — | 一致 |
| 美国 | 政策 | DFEDTARU | 最新一期 | 4.0 | 4.0 | 2026-11 | 2026-11 | 4.0 | 2026-11 | — | — | 一致 |
| 美国 | 政策 | DFF | 12个月前 | 3.88 | 3.88 | 2025-11 | 2025-11 | 3.88 | 2025-11 | — | — | 一致 |
| 美国 | 政策 | DFF | 3个月前 | 3.63 | 3.63 | 2026-08 | 2026-08 | 3.63 | 2026-08 | — | — | 一致 |
| 美国 | 政策 | DFF | 最新一期 | 3.88 | 3.88 | 2026-11 | 2026-11 | 3.88 | 2026-11 | — | — | 一致 |
| 中国 | 增长 | CN_PMI_MFG | 12个月前 | 49.0 | 49.0 | 2025-10 | 2025-10 | 49.0 | 2025-10 | — | — | 一致 |
| 中国 | 增长 | CN_PMI_MFG | 3个月前 | 49.2 | 49.2 | 2026-07 | 2026-07 | 49.2 | 2026-07 | — | — | 一致 |
| 中国 | 增长 | CN_PMI_MFG | 最新一期 | 49.3 | 49.3 | 2026-10 | 2026-10 | 49.3 | 2026-10 | — | — | 一致 |
| 中国 | 通胀 | CN_CPI_YOY | 12个月前 | 0.2 | 0.2 | 2025-10 | 2025-10 | 0.2 | 2025-10 | — | — | 一致 |
| 中国 | 通胀 | CN_CPI_YOY | 3个月前 | 0.5 | 0.5 | 2026-07 | 2026-07 | 0.5 | 2026-07 | — | — | 一致 |
| 中国 | 通胀 | CN_CPI_YOY | 最新一期 | 0.7 | 0.7 | 2026-10 | 2026-10 | 0.7 | 2026-10 | — | — | 一致 |
| 中国 | 通胀 | CN_PPI_YOY | 12个月前 | -2.1 | -2.1 | 2025-10 | 2025-10 | -2.1 | 2025-10 | — | — | 一致 |
| 中国 | 通胀 | CN_PPI_YOY | 3个月前 | 3.5 | 3.5 | 2026-07 | 2026-07 | 3.5 | 2026-07 | — | — | 一致 |
| 中国 | 通胀 | CN_PPI_YOY | 最新一期 | 5.7 | 5.7 | 2026-10 | 2026-10 | 5.7 | 2026-10 | — | — | 一致 |
| 中国 | 政策 | CN_POLICY_OVERNIGHT | 12个月前 | — | — | — | — | 缺席(no_published_observation_on_or_before_anchor) | — | — | — | 诚实缺席格(不计点) |
| 中国 | 政策 | CN_POLICY_OVERNIGHT | 3个月前 | — | — | — | — | 缺席(no_published_observation_on_or_before_anchor) | — | — | — | 诚实缺席格(不计点) |
| 中国 | 政策 | CN_POLICY_OVERNIGHT | 最新一期 | 1.25 | 1.25 | 2026-11 | 2026-11 | 1.25 | 2026-11 | — | — | 一致 |
| 中国 | 政策 | CN_OMO_7D | 12个月前 | 1.4 | 1.4 | 2025-11 | 2025-11 | 1.4 | 2025-11 | — | — | 一致 |
| 中国 | 政策 | CN_OMO_7D | 3个月前 | 1.4 | 1.4 | 2026-08 | 2026-08 | 1.4 | 2026-08 | — | — | 一致 |
| 中国 | 政策 | CN_OMO_7D | 最新一期 | 1.4 | 1.4 | 2026-10 | 2026-10 | 1.4 | 2026-10 | — | — | 一致 |
| 中国 | 政策 | CN_LPR_1Y | 12个月前 | 3.0 | 3.0 | 2025-11 | 2025-11 | 3.0 | 2025-11 | — | — | 一致 |
| 中国 | 政策 | CN_LPR_1Y | 3个月前 | 3.0 | 3.0 | 2026-08 | 2026-08 | 3.0 | 2026-08 | — | — | 一致 |
| 中国 | 政策 | CN_LPR_1Y | 最新一期 | 3.0 | 3.0 | 2026-11 | 2026-11 | 3.0 | 2026-11 | — | — | 一致 |
| 欧元区 | 增长 | EA_REAL_GDP_YOY | 12个月前 | 1.11 | 1.11 | 2025-07 | 2025-07 | 1.11 | 2025-07 | — | — | 一致 |
| 欧元区 | 增长 | EA_REAL_GDP_YOY | 3个月前 | 1.19 | 1.19 | 2026-04 | 2026-04 | 1.19 | 2026-04 | — | — | 一致 |
| 欧元区 | 增长 | EA_REAL_GDP_YOY | 最新一期 | 1.28 | 1.28 | 2026-07 | 2026-07 | 1.28 | 2026-07 | — | — | 一致 |
| 欧元区 | 通胀 | EA_HICP_YOY | 12个月前 | 2.1 | 2.1 | 2025-10 | 2025-10 | 2.1 | 2025-10 | — | — | 一致 |
| 欧元区 | 通胀 | EA_HICP_YOY | 3个月前 | 2.9 | 2.9 | 2026-07 | 2026-07 | 2.9 | 2026-07 | — | — | 一致 |
| 欧元区 | 通胀 | EA_HICP_YOY | 最新一期 | 4.0 | 4.0 | 2026-10 | 2026-10 | 4.0 | 2026-10 | — | — | 一致 |
| 欧元区 | 政策 | ECB_MRO | 12个月前 | 2.15 | 2.15 | 2025-06 | 2025-06 | 2.15 | 2025-06 | — | — | 一致 |
| 欧元区 | 政策 | ECB_MRO | 3个月前 | 2.4 | 2.4 | 2026-06 | 2026-06 | 2.4 | 2026-06 | — | — | 一致 |
| 欧元区 | 政策 | ECB_MRO | 最新一期 | 2.65 | 2.65 | 2026-09 | 2026-09 | 2.65 | 2026-09 | — | — | 一致 |
| 欧元区 | 政策 | ECB_DFR | 12个月前 | 2.0 | 2.0 | 2025-06 | 2025-06 | 2.0 | 2025-06 | — | — | 一致 |
| 欧元区 | 政策 | ECB_DFR | 3个月前 | 2.25 | 2.25 | 2026-06 | 2026-06 | 2.25 | 2026-06 | — | — | 一致 |
| 欧元区 | 政策 | ECB_DFR | 最新一期 | 2.5 | 2.5 | 2026-09 | 2026-09 | 2.5 | 2026-09 | — | — | 一致 |
| 日本 | 增长 | JP_REAL_GDP_YOY | 12个月前 | 0.63 | 0.63 | 2025-07 | 2025-07 | 0.63 | 2025-07 | — | — | 一致 |
| 日本 | 增长 | JP_REAL_GDP_YOY | 3个月前 | 0.8 | 0.8 | 2026-04 | 2026-04 | 0.8 | 2026-04 | — | — | 一致 |
| 日本 | 增长 | JP_REAL_GDP_YOY | 最新一期 | 1.16 | 1.16 | 2026-07 | 2026-07 | 1.16 | 2026-07 | — | — | 一致 |
| 日本 | 通胀 | JP_CPI_YOY | 12个月前 | 2.99 | 2.99 | 2025-10 | 2025-10 | 2.99 | 2025-10 | — | — | 一致 |
| 日本 | 通胀 | JP_CPI_YOY | 3个月前 | 1.97 | 1.97 | 2026-07 | 2026-07 | 1.97 | 2026-07 | — | — | 一致 |
| 日本 | 通胀 | JP_CPI_YOY | 最新一期 | 2.44 | 2.44 | 2026-10 | 2026-10 | 2.44 | 2026-10 | — | — | 一致 |
| 日本 | 通胀 | JP_CPI_TOKYO_YOY | 12个月前 | — | — | — | — | 缺席(no_published_observation_on_or_before_anchor) | — | — | — | 诚实缺席格(不计点) |
| 日本 | 通胀 | JP_CPI_TOKYO_YOY | 3个月前 | 1.85 | 1.85 | 2026-07 | 2026-07 | 1.85 | 2026-07 | — | — | 一致 |
| 日本 | 通胀 | JP_CPI_TOKYO_YOY | 最新一期 | 2.73 | 2.73 | 2026-10 | 2026-10 | 2.73 | 2026-10 | — | — | 一致 |
| 日本 | 政策 | JP_POLICY_RATE | 12个月前 | 0.477 | 0.477 | 2025-10 | 2025-10 | 0.477 | 2025-10 | — | — | 一致 |
| 日本 | 政策 | JP_POLICY_RATE | 3个月前 | 0.978 | 0.978 | 2026-07 | 2026-07 | 0.978 | 2026-07 | — | — | 一致 |
| 日本 | 政策 | JP_POLICY_RATE | 最新一期 | 1.227 | 1.227 | 2026-10 | 2026-10 | 1.227 | 2026-10 | — | — | 一致 |

「值: 报告」=判断档 anchor_echo 回贴值;「引擎格值」=report.json research_plan.point_values.cells;「同比」=水平序列的同比派生值(直算自 series_store 同月一年前,报告侧为引擎格 derived_yoy_pct),无同比行的格为同比序列本身。

锚点节其余行(非逐格行):

| 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|
| JP_POLICY_TARGET not in registry | snapshot series_store keys | False | absent | 一致 | judgment: plan metric not in registry |
| CN_POLICY_OVERNIGHT no obs before 3m anchor | series_store CN_POLICY_OVERNIGHT | 不可得(null) | absent | 一致 |  |
| CN_POLICY_OVERNIGHT first obs = 2026-11-02 | series_store CN_POLICY_OVERNIGHT dates | 2026-11-02 | 2026-11-02 | 一致 | headline: 2026-11-02 anchor switch |
| CN_POLICY_OVERNIGHT flat since first obs | series_store CN_POLICY_OVERNIGHT values | [1.25] | single value 1.25 | 一致 | flat at first observation |
| JP_CPI_TOKYO_YOY no published obs before 12m anchor | series_store JP_CPI_TOKYO_YOY | 不可得(null) | absent | 一致 |  |
| no observation after cutoff | series_store all series max date | 2026-11-23(SPX) | <=2026-11-23 | 一致 | research_as_of=2026-11-23T22:53:47+08:00 |
| snapshot research_as_of date | snapshot research_as_of | 2026-11-23 | 2026-11-23 | 一致 |  |
| snapshot target_date | snapshot target_date | 20261123 | 20261123 | 一致 |  |

### 5.3 转折候选面(由台账 candidate 行生成)

窗口=引擎候选窗(相隔三个观测的最大变化所在月);「引擎」=report.json turning_candidates.candidates / 研判席工单 turning_candidates_top9;「直算」=本席按同一规则自冻结快照重算。唯一偏离见第 8 行。

| 序 | 指标 | 地区/维度 | 窗口: 引擎 | 窗口: 直算 | 前值: 引擎 | 前值: 直算 | 后值: 引擎 | 后值: 直算 | Δ: 引擎 | Δ: 直算 | 一致与否 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CN_PPI_YOY | 中国/通胀 | 2026-02..2026-05 | 2026-02..2026-05 | -0.9 | -0.9 | 3.9 | 3.9 | 4.8 | 4.8 | 一致 |
| 2 | CN_PMI_MFG | 中国/增长 | 2026-02..2026-05 | 2026-02..2026-05 | -2.3904 | -2.3904 | 1.0101 | 1.0101 | 3.4005 | 3.4005 | 一致 |
| 3 | CPI | 美国/通胀 | 2026-02..2026-05 | 2026-02..2026-05 | 2.434 | 2.434 | 4.1666 | 4.1666 | 1.7326 | 1.7326 | 一致 |
| 4 | JP_CPI_YOY | 日本/通胀 | 2025-11..2026-02 | 2025-11..2026-02 | 2.9 | 2.9 | 1.27 | 1.27 | -1.63 | -1.63 | 一致 |
| 5 | EA_HICP_YOY | 欧元区/通胀 | 2026-02..2026-05 | 2026-02..2026-05 | 1.9 | 1.9 | 3.2 | 3.2 | 1.3 | 1.3 | 一致 |
| 6 | JP_CPI_TOKYO_YOY | 日本/通胀 | 2026-06..2026-09 | 2026-06..2026-09 | 1.6 | 1.6 | 2.69 | 2.69 | 1.09 | 1.09 | 一致 |
| 7 | CN_CPI_YOY | 中国/通胀 | 2026-01..2026-04 | 2026-01..2026-04 | 0.2 | 0.2 | 1.2 | 1.2 | 1.0 | 1.0 | 一致 |
| 8 | INDPRO | 美国/增长 | 2025-11..2026-02 | 2025-11..2026-02 | 1.7543 | 1.7543 | 0.7972 | 0.7972 | -0.9571 | -0.9571 | 一致 |
| 9 | CORE_CPI | 美国/通胀 | 2026-05..2026-08 | 2026-05..2026-08 | 2.8229 | 2.8229 | 2.4462 | 2.4462 | -0.3767 | -0.3768 | 偏离(delta) |

候选面相关的其余 4 行:

| 点 | 出处键 | 直算值 | 报告值 | 一致与否 | 备注 |
|---|---|---|---|---|---|
| candidate face sorted by \|delta\| descending (9 rows) | MAP_REPORT.md 引擎转折候选面行序 | True | True | 一致 |  |
| turnings[1] CN_PMI_MFG z口径 2026-02 (judgment quote) | series_store CN_PMI_MFG 指数水平同比% | -2.3904 | -2.3904 | 一致 | 判断档 turnings[1].first_mover 「z口径 -2.3904→1.0101」 |
| turnings[1] CN_PMI_MFG z口径 2026-05 (judgment quote) | series_store CN_PMI_MFG 指数水平同比% | 1.0101 | 1.0101 | 一致 | 判断档 turnings[1].first_mover 「z口径 -2.3904→1.0101」 |
| turnings[0] 'CPI = 候选面最大美欧值' (\|delta\| max among US+EA candidates) | MAP_REPORT.md 引擎转折候选面 US/EA 行 | True | True | 一致 | US/EA \|Δ\|=[1.7326, 1.3, 0.9571, 0.3767] |

### 5.4 同步面(由台账 sync 行生成)

「标签: 引擎」=report.json steps[60] S5_compare 信封的地区×维度同步面(相对美国);「标签: 直算」=本席自 series_store 重算;「判断档通胀维标签」=判断档 history_periods[*].other_regions_sync 文字所引标签(报告),「直算」=按引擎面规则应取的通胀维标签,只列在通胀行;美国为参照系,其自身无同步标签。

| 段 | 地区 | 维度 | 标签: 直算 | 标签: 引擎 | 底层读数变化(席位直算,信息行) | 判断档通胀维标签: 直算 | 判断档通胀维标签: 报告 | 一致与否 |
|---|---|---|---|---|---|---|---|---|
| 2025-03 | 美国 | 增长 | 下行 | 下行 | -0.306 | — | — | 一致 |
| 2025-03 | 美国 | 通胀 | 上行 | 上行 | 0.08211 | — | — | 一致 |
| 2025-03 | 美国 | 政策 | 持平 | 持平 | 0 | — | — | 一致 |
| 2025-03 | 中国 | 增长 | 分化 | 分化 | 0.4 | — | — | 一致 |
| 2025-03 | 中国 | 通胀 | 分化 | 分化 | -0.9 | 分化 | 分化 | 一致 |
| 2025-03 | 中国 | 政策 | 同步 | 同步 | 0 | — | — | 一致 |
| 2025-03 | 欧元区 | 增长 | 分化 | 分化 | 0.25 | — | — | 一致 |
| 2025-03 | 欧元区 | 通胀 | 分化 | 分化 | -0.1 | 分化 | 分化 | 一致 |
| 2025-03 | 欧元区 | 政策 | 分化 | 分化 | -0.5 | — | — | 一致 |
| 2025-03 | 日本 | 增长 | 同步 | 同步 | -0.1 | — | — | 一致 |
| 2025-03 | 日本 | 通胀 | 同步 | 同步 | 0.74 | 同步 | 同步 | 一致 |
| 2025-03 | 日本 | 政策 | 分化 | 分化 | 0.251 | — | — | 一致 |
| 2022-06 | 美国 | 增长 | 下行 | 下行 | -1.843 | — | — | 一致 |
| 2022-06 | 美国 | 通胀 | 上行 | 上行 | 0.6009 | — | — | 一致 |
| 2022-06 | 美国 | 政策 | 上行 | 上行 | 1.25 | — | — | 一致 |
| 2022-06 | 中国 | 增长 | 分化 | 分化 | 0.7 | — | — | 一致 |
| 2022-06 | 中国 | 通胀 | 同步 | 同步 | 1.2 | 同步 | 同步 | 一致 |
| 2022-06 | 中国 | 政策 | 分化 | 分化 | 0 | — | — | 一致 |
| 2022-06 | 欧元区 | 增长 | 同步 | 同步 | -0.1 | — | — | 一致 |
| 2022-06 | 欧元区 | 通胀 | 同步 | 同步 | 0.7 | 同步 | 同步 | 一致 |
| 2022-06 | 欧元区 | 政策 | 分化 | 分化 | 0 | — | — | 一致 |
| 2022-06 | 日本 | 增长 | 同步 | 同步 | -1.65 | — | — | 一致 |
| 2022-06 | 日本 | 通胀 | 同步 | 同步 | 1.51 | 同步 | 同步 | 一致 |
| 2022-06 | 日本 | 政策 | 分化 | 分化 | 0 | — | — | 一致 |
| 2023-10 | 美国 | 增长 | 上行 | 上行 | 0.4479 | — | — | 一致 |
| 2023-10 | 美国 | 通胀 | 上行 | 上行 | 0.6166 | — | — | 一致 |
| 2023-10 | 美国 | 政策 | 持平 | 持平 | 0 | — | — | 一致 |
| 2023-10 | 中国 | 增长 | 同步 | 同步 | 0.2 | — | — | 一致 |
| 2023-10 | 中国 | 通胀 | 分化 | 分化 | 0 | 分化 | 分化 | 一致 |
| 2023-10 | 中国 | 政策 | 分化 | 分化 | -0.1 | — | — | 一致 |
| 2023-10 | 欧元区 | 增长 | 分化 | 分化 | -0.74 | — | — | 一致 |
| 2023-10 | 欧元区 | 通胀 | 分化 | 分化 | -2.4 | 分化 | 分化 | 一致 |
| 2023-10 | 欧元区 | 政策 | 分化 | 分化 | 0.5 | — | — | 一致 |
| 2023-10 | 日本 | 增长 | 分化 | 分化 | -0.89 | — | — | 一致 |
| 2023-10 | 日本 | 通胀 | 分化 | 分化 | -0.25 | 分化 | 分化 | 一致 |
| 2023-10 | 日本 | 政策 | 分化 | 分化 | 0.012 | — | — | 一致 |

### 5.5 历史事后段(由台账 history 行生成)

每格=「报告值 / 直算值」;报告值=判断档 ex_post 文字(两位小数、带符号),直算值=series_store 自然月末→锚+N 月月末的变化率(%)或差(pp),未舍入值见第 1.2 节;99 格全部一致。

| 指标(单位) | 2025-03 3个月 | 2025-03 6个月 | 2025-03 12个月 | 2022-06 3个月 | 2022-06 6个月 | 2022-06 12个月 | 2023-10 3个月 | 2023-10 6个月 | 2023-10 12个月 |
|---|---|---|---|---|---|---|---|---|---|
| DFEDTARU(pp) | +0.00 / 0.0 | -0.25 / -0.25 | -0.75 / -0.75 | +1.50 / 1.5 | +2.75 / 2.75 | +3.50 / 3.5 | +0.00 / 0.0 | +0.00 / 0.0 | -0.50 / -0.5 |
| UNEMPLOYMENT(pp) | -0.10 / -0.1 | +0.20 / 0.2 | +0.10 / 0.1 | -0.10 / -0.1 | -0.10 / -0.1 | +0.00 / 0.0 | -0.20 / -0.2 | +0.00 / 0.0 | +0.20 / 0.2 |
| CPI(%) | +0.52 / 0.516 | +1.39 / 1.3947 | +3.29 / 3.286 | +0.47 / 0.4719 | +1.31 / 1.3138 | +3.07 / 3.0706 | +0.65 / 0.6506 | +1.73 / 1.7313 | +2.58 / 2.5788 |
| INDPRO(%) | +0.43 / 0.4336 | +0.62 / 0.6211 | +0.69 / 0.6861 | +0.27 / 0.271 | -1.24 / -1.239 | -0.89 / -0.8893 | -1.24 / -1.2408 | -0.22 / -0.2244 | -0.99 / -0.9947 |
| SPX(%) | +10.57 / 10.5687 | +19.18 / 19.1846 | +16.33 / 16.3345 | -5.28 / -5.2771 | +1.43 / 1.4297 | +17.57 / 17.5676 | +15.54 / 15.5432 | +20.07 / 20.0746 | +36.04 / 36.0449 |
| NIKKEI225(%) | +13.67 / 13.6726 | +26.15 / 26.153 | +43.37 / 43.3667 | -1.73 / -1.7271 | -1.13 / -1.1311 | +25.75 / 25.7492 | +17.59 / 17.5893 | +24.46 / 24.4559 | +26.65 / 26.6452 |
| DAX(%) | +7.88 / 7.8784 | +7.75 / 7.748 | +2.33 / 2.3306 | -5.24 / -5.2364 | +8.92 / 8.9162 | +26.32 / 26.3156 | +14.13 / 14.1349 | +21.08 / 21.0787 | +28.81 / 28.8123 |
| SHCOMP(%) | +3.26 / 3.258 | +16.40 / 16.3991 | +16.67 / 16.6714 | -11.01 / -11.0111 | -9.10 / -9.1025 | -5.78 / -5.7833 | -7.63 / -7.6264 | +2.85 / 2.8506 | +8.65 / 8.6477 |
| GOLD_F(%) | +5.92 / 5.921 | +24.03 / 24.0297 | +48.83 / 48.828 | -7.49 / -7.4863 | +1.05 / 1.0458 | +6.76 / 6.7559 | +2.71 / 2.7127 | +15.47 / 15.4741 | +37.86 / 37.8579 |
| DXY(%) | -7.03 / -7.0339 | -6.18 / -6.1798 | -4.08 / -4.0783 | +7.10 / 7.0971 | -1.12 / -1.1176 | -1.70 / -1.7003 | -3.18 / -3.1783 | -0.41 / -0.4125 | -2.51 / -2.5127 |
| UST_10Y(pp) | +0.01 / 0.01 | -0.07 / -0.07 | +0.07 / 0.07 | +0.85 / 0.85 | +0.90 / 0.9 | +0.83 / 0.83 | -0.89 / -0.89 | -0.19 / -0.19 | -0.60 / -0.6 |

引擎事后块(引擎口径,起点为锚后首个观测,与上表自然月末口径不同;同一资产两口径数值不可直接互比):

每格=「报告值 / 直算值」(%,引擎口径: 锚后首个观测→锚+N 月后首个观测);报告值=report.json steps[61] 相似检索面事后块(研判席工单 ex_post_offsets),直算值=本席按引擎口径自 series_store 重算;48 格全部一致。

| 资产 | 2025-03 1个月 | 2025-03 3个月 | 2025-03 6个月 | 2025-03 12个月 | 2022-06 1个月 | 2022-06 3个月 | 2022-06 6个月 | 2022-06 12个月 | 2023-10 1个月 | 2023-10 3个月 | 2023-10 6个月 | 2023-10 12个月 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPX | -1.136321 / -1.136321 | 10.152197 / 10.152197 | 18.735613 / 18.735613 | 15.896309 / 15.896309 | 7.972121 / 7.972121 | -6.266386 / -6.266386 | 0.370424 / 0.370424 | 16.339761 / 16.339761 | 7.785532 / 7.785532 | 14.34191 / 14.34191 | 18.82625 / 18.82625 | 34.630459 / 34.630459 |
| UST_10Y | 0.0 / 0.0 | 0.07 / 0.07 | -0.01 / -0.01 | 0.13 / 0.13 | -0.21 / -0.21 | 0.95 / 0.95 | 1.0 / 1.0 | 0.93 / 0.93 | -0.4 / -0.4 | -0.78 / -0.78 | -0.08 / -0.08 | -0.49 / -0.49 |
| DXY | -4.594284 / -4.594284 | -7.078462 / -7.078462 | -6.224827 / -6.224827 | -4.124307 / -4.124307 | 0.722849 / 0.722849 | 6.638771 / 6.638771 | -1.540805 / -1.540805 | -2.120977 / -2.120977 | -3.162422 / -3.162422 | -3.37762 / -3.37762 | -0.617511 / -0.617511 | -2.713318 / -2.713318 |
| GOLD_F | 5.502228 / 5.502228 | 5.139859 / 5.139859 | 23.115065 / 23.115065 | 47.730454 / 47.730454 | -2.142658 / -2.142658 | -7.188454 / -7.188454 | 1.371077 / 1.371077 | 7.099641 / 7.099641 | 2.545911 / 2.545911 | 3.064146 / 3.064146 | 15.869177 / 15.869177 | 38.329562 / 38.329562 |

### 5.6 工单四子问与内容的对应

| 子问 | 对应内容 | 相称性 |
|---|---|---|
| 四地在 12 个月前、3 个月前、最新一期的增长、通胀、货币政策环境 | reader_map.regions[0..3] 的分维走位文字与 anchor_echo(63 值),读者报告四地三时点对照表(22 格×3 锚) | 四地×三维×三锚全部在场,3 格诚实缺席;数值全部命中 |
| 过去一年最重要的三个转折、谁先变、谁跟进或背离 | reader_map.turnings[0..2](指标、窗口、前值后值、first_mover、follow_or_diverge)、turning_supplement(东京 CPI 引擎补选)、引擎候选面 top9、政策事件簇 | 三个转折各有数值与同窗/背离叙述;「谁先变」在月频分辨率下如实答「先后未定」 |
| 证据最充分的传导机制、其他解释、区分指标 | transmission[0] TR1 三环(各含主/竞争预期、区分指标、对质判断)、transmission[1] TR2、l3.mechanism_chains、C1 三解释 | 主链与竞争链均有,区分指标逐环给出 |
| 历史上结构最像的时期、当时其他经济体是否同步、随后 3/6/12 个月实际走向 | reader_map.history_periods[0..2](距离、贡献、差异、同步性、事后 3/6/12 月 11 个指标)、C2 | 三段各 11 指标×3 窗,同步性给出通胀维标签,事后段标明非预测 |

## 6. 问题清单

定级依据(规程第 5 节): MAJOR = 数字/日期/方向错或与证据相左、缺基期却给同比、以相邻口径冒充、事后信息冒充当时可知、结论超出证据且无标注、证伪条件不可观测;MINOR = 口径或披露可改进但不改变结论;NIT = 行文。本席未发现任何 MAJOR。关于唯一数值偏离(MINOR-9)为何不定 MAJOR: 面值与未舍入直算值相差 0.0000789,不足端点自身展示精度(0.0001)的一个单位,方向、量级与行序均不变,且位于引擎渲染面而非受审判断文字;按「数字错」的字面不成立,按「口径未注明」成立,故记 MINOR 并在 recompute_mismatches 中如实计 1。

**MAJOR(0 条)**: 无——must_fix 为空。

**MINOR(9 条;不构成阻断)**

- **MINOR-1**
  - 位置: agent_judgment.json reader_map.transmission[0].links[0].causal_hypothesis(对质注记)与 face_off_verdict;transmission[1].links[0].face_off_verdict;quality_gate_notes[1];MAP_REPORT.md「主解释 vs 竞争解释(对质表)」第 1、4 行
  - 问题: 对质表四环一律「尚不能区分」,与表下自述口径(预期分立且观测在场才可裁;观测缺席或预期未分立才记尚不能区分)不完全一致。第1环: 区分指标 BRENT_F 月末口径 2026-02-27 72.48→2026-03-31 118.35→2026-05-29 92.05(首尾 +27.00%),主解释预注册的「同窗显著上行」成立,竞争解释预注册的「大体持平」未获支持;CORE_CPI 同窗 2.47→2.82 对两解释均相容,不是区分观测。正文写「布伦特 03 冲至 118.35 后于 05 回落至首月末附近(未持平)」,已自注未持平,但「首月末附近」(92.05 对 72.48,+27.00%)与同行「首尾 +27.00%」措辞相抵(至 2026-06 月末 72.92 才回到首月末水平)。第4环(TR2): 主解释预期「风险资产收缩与日元走强同现」在同窗未获支持(USDJPY 156.49→159.35,+1.82%),正文已写「分量应下调」却仍记「尚不能区分」。对质表「已有观测」列四行均为引擎近 30 日面(第1环 BRENT_F 116.72→88.19,−24.44%),与该行预注册窗(2026-02 至 2026-05)不对应。属偏保守的少判,未夸大结论,故记 MINOR。
  - 原句: 「两侧各有相容观测，尚不能区分。」
  - 改句(建议): 「区分指标面倾向主解释(供给侧): BRENT_F 月末口径 2026-02 72.48→2026-05 92.05(首尾 +27.00%),竞争解释预期的『大体持平』未获支持;核心CPI同比同窗 2.47→2.82 对两解释均相容(非区分观测)。『能源→生产价格→消费价格』的因果传导仍为【假设】。TR2 第4环同步改为『主解释在同窗未获支持(SPX −5.51% 而 USDJPY +1.82%),倾向竞争解释(逐日面待核)』。」

- **MINOR-2**
  - 位置: agent_judgment.json l3.mechanism_chains[0].links[1].text;reader_map.transmission[0].links[1].causal_hypothesis
  - 问题: 「因通胀续升而收紧」与决议前可见数据不完全吻合、「动机环证据减弱」只以美国 CPI 同比论证,却施用于欧央行与日本央行的 9 月决议。决议时点前可见的本地区通胀处于回升段: 欧央行 2026-09-10 决议前可见 EA_HICP_YOY 2026-08 观测 3.2(高于 2026-07 的 2.9,与 2026-05 的 3.2 持平);日本央行 2026-09-18 决议前可见 JP_CPI_YOY 2026-07 观测 1.97(高于 2026-04 的 1.38)。该判断对美联储成立(可见 CPI 2026-08 观测 3.353、CORE_PCE 2026-07 观测 2.995,均低于 2026-05 高点 4.1666/3.1617)。结论(动机不可验证,E3)不变。
  - 原句: 「『因通胀续升而收紧』与 9 月决议前的可见数据不完全吻合，动机环证据减弱(仍不可验证)。」
  - 改句(建议): 「『因通胀续升而收紧』对美联储与决议前可见数据不完全吻合(CPI 2026-08 观测 3.35、CORE_PCE 2026-07 观测 3.00,均低于 2026-05 高点 4.17/3.16);对欧央行与日本央行,决议前可见的本地区通胀处于回升段(HICP 2026-08 观测 3.2、日本CPI 2026-07 观测 1.97),与收紧动机相容但同样不可验证。」

- **MINOR-3**
  - 位置: agent_judgment.json l3.contradictions[0].statement(首句『过去12个月…同向共动』);l3.mechanism_chains[0].links[2].text 与 links[3].text;reader_map.transmission[0].links[2].observed_fact 与 causal_hypothesis
  - 问题: 同一环内利率腿用 12 个月窗(名义 +91bp、实际 +102bp),资产腿用近 1 个月窗,未披露 12 个月窗内股指与实际利率同向上行: 共同交易日 2025-11-19→2026-11-19 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93%,而 TIPS_10Y +102bp。共动方向只在近 1 个月(TIPS_10Y +11bp、SPX −6.96%)与近 3 个月(TIPS_10Y +53bp、SPX −6.90%)窗成立。C1 与标题已把资产收缩限定为「近月」,不构成方向错,但属未披露的反向事实。
  - 原句: 「资产环【E2,缺环为假设】: 近1个月(2026-10-23→2026-11-19/20/23)SPX -5.51%、NIKKEI225 -9.98%、GOLD_F -8.05%、DXY +2.23%、VIX 19.45→27.01(其中 SPX、GOLD_F、DXY、VIX 为 2026-11-23 盘中快照、非收盘价；同日收盘口径 2026-10-23→2026-11-20 标普500指数 -9.36%、VIX +84.52%),与『实际利率上行压制长久期/无现金流资产、推升美元』的机制相容;」
  - 改句(建议): 「在资产环补一句: 「同窗12个月(共同交易日 2025-11-19→2026-11-19)SPX +8.03%、NIKKEI225 +22.47%,与实际利率 +102bp 同向上行——『实际利率上行压制风险资产』的共动只在近1至3个月窗成立,12个月窗不成立」。」

- **MINOR-4**
  - 位置: agent_judgment.json reader_map.history_periods[0..2].other_regions_sync(引导词 部分同步/同步/不同步)
  - 问题: 三段同步性的引导词与所列标签只覆盖通胀维,工单「当时其他经济体是否同步」未限定维度。按引擎地区×维度同步面: 2022-06 段九格中五格同步(通胀三地同步;增长: 中国分化、欧元区同步、日本同步;政策: 三地均分化——美国 +125bp 而三地持平),2025-03 段三格同步,2023-10 段一格同步。句内已注明「通胀维方向,相对美国」且与引擎面 9/9 一致,MAP_REPORT 紧随其后渲染引擎全维表,不构成「叙述与面冲突」。
  - 原句: 「同步: 截至2022-06-30已发布数据显示,欧元区HICP同比2022-05为8.1、日本CPI同比2022-05为2.46、中国PPI同比2022-05为6.4、中国CPI同比2022-05为2.1——引擎同步面(通胀维方向,相对美国): 中国同步、欧元区同步、日本同步。」
  - 改句(建议): 「同步(仅通胀维): 截至2022-06-30已发布数据显示,……——引擎同步面(通胀维方向,相对美国): 中国同步、欧元区同步、日本同步;增长维: 中国分化、欧元区与日本同步;政策维: 三地均分化(美国窗内 +125bp,三地持平)。」

- **MINOR-5**
  - 位置: agent_judgment.json l4.scenarios[0].rows.trigger.condition 与 l4.scenarios[1].rows.trigger.condition
  - 问题: 两情景触发条件均写「决议日见发布日历实录」(欧央行/美联储),而冻结发布日历 18 条中无美联储、欧央行条目(日本央行 2 条),quality_gate_notes[2] 与传导面正文亦自述该事实——同档内自相矛盾。触发条件本身仍可观测(序列变更日按引擎惯例回推,或待日历补录)。
  - 原句: 「美国2026-11或2026-12月CPI同比继续≥3.5,或欧央行/美联储再加息(决议日见发布日历实录)」
  - 改句(建议): 「美国2026-11或2026-12月CPI同比继续≥3.5,或欧央行/美联储再加息(生效日=DFEDTARU/ECB_DFR 序列变更日,决议日按引擎惯例自生效日回推【推断】;冻结发布日历暂无两家实录条目)」

- **MINOR-6**
  - 位置: agent_judgment.json l3.contradictions[2].evidence_refs[3] 与 competing_explanations[2]
  - 问题: C3 引用 USDCNY@2026-11-23 但陈述与解释均未使用;解释C(汇率/资本流动目标约束)被整体标为不可检验。库内无中国资本流动序列属实,但汇率腿可部分检验: USDCNY 2025-11-19 7.1075→2026-11-19 6.6676(12 个月 −6.19%)、2026-11-23 6.6542,人民币窗内升值,与「防贬值/资本外流压力制约加息」的读法方向不相容。引擎契约面亦披露该项引用「未在文本展开」。
  - 原句: 「解释C: 汇率/资本流动目标约束政策选择——引擎面无中国资本流动序列,该解释当前不可检验,标注【尚未验证】」
  - 改句(建议): 「解释C: 汇率/资本流动目标约束政策选择——引擎面无中国资本流动序列,该解释当前不可裁决,标注【尚未验证】;汇率腿的可见事实: USDCNY 12 个月 −6.19%(7.1075→6.6676,2025-11-19→2026-11-19),人民币窗内升值,不支持『贬值/外流压力制约加息』的读法。」

- **MINOR-7**
  - 位置: agent_judgment.json reader_map.headline_conclusion;l3.mechanism_chains[0].links[0].text;reader_map.transmission[0].links[0].observed_fact
  - 问题: 「美欧中通胀同窗回升(2026-02→2026-05)」的中国腿为 PPI(−0.9→3.9),正文逐处点名指标,无冒充;但同窗中国 CPI 同比为 1.3→1.2(2026-02→2026-05,其间 2026-03 1.0、2026-04 1.2),消费价格并未共振。标题用统称「通胀」,建议在中国处标明「生产价格」。
  - 原句: 「美欧中通胀在2026-02至2026-05同窗共振回升(月频分辨率下先后未定)」
  - 改句(建议): 「美欧通胀与中国生产价格(PPI)在2026-02至2026-05同窗共振回升(美国CPI、欧元区HICP、中国PPI;中国CPI同窗持平于1.0–1.3;月频分辨率下先后未定)」

- **MINOR-8**
  - 位置: agent_judgment.json reader_map.regions[0..3].from_to(增长维)与 regions[*].anchor_echo 的季频 GDP 值;quality_gate_notes[0]
  - 问题: 三地季频 GDP 三锚值(美国 2.42/2.19/2.07 由水平 23884.563/24408.011/24611.077 直算;欧元区 1.11/1.19/1.28;日本 0.63/0.80/1.16)在引擎点值面的口径为「事后回顾(最新修订值,非当时首发值)」,MAP_REPORT 引擎表已注明;判断档正文与质量注记未对这三行注明修订口径(类比段与 2023-10 段已注明)。数值与方向不受影响。
  - 原句: 「增长: 实际GDP同比 2.42→2.19→2.07(观测 2025-04→2026-04→2026-07,水平 23884.563→24408.011→24611.077 十亿美元,即2025Q2→2026Q2→2026Q3)温和放缓」
  - 改句(建议): 「增长: 实际GDP同比 2.42→2.19→2.07(观测 2025-04→2026-04→2026-07,水平 23884.563→24408.011→24611.077 十亿美元,即2025Q2→2026Q2→2026Q3;最新修订值、事后回顾口径,非当时首发值)温和放缓」

- **MINOR-9**
  - 位置: MAP_REPORT.md 引擎转折候选面(确定性排序表)CORE_CPI 行 Δ 列(引擎渲染面;判断档正文未引用该 Δ)
  - 问题: Δ -0.3767 等于两个四位小数端点之差(2.4462−2.8229);按冻结快照未舍入值直算 CORE_CPI 同比 2026-05 为 2.8229420636、2026-08 为 2.4461631786,差 -0.3767788850,四位小数应为 -0.3768。面值与直算值相差 0.0000789,不足端点自身展示精度(0.0001)的一个单位,方向、量级与行序(末位)均不变;其余 8 项候选的 Δ 与未舍入直算逐位一致。属差值舍入口径未注明,不构成数值错误,故记 MINOR 而非 MAJOR。
  - 原句: 「\| US \| inflation \| CORE_CPI \| 2026-05..2026-08 \| 2.8229→2.4462 \| -0.3767 \|」
  - 改句(建议): 「\| US \| inflation \| CORE_CPI \| 2026-05..2026-08 \| 2.8229→2.4462 \| -0.3768 \|(或保留 -0.3767 并注明「Δ 为端点四位小数相减值」)」

**NIT(11 条;不构成阻断)**

- **NIT-1**
  - 位置: agent_judgment.json reader_map.transmission[1].links[0].causal_hypothesis
  - 问题: 正文称逐日共动面「本档未做」。冻结快照内可得,本席补核(盘中口径,2026-10-27→2026-11-23,21 个交易日): SPX 与 USDJPY 日变动相关系数 0.191;SPX 下跌 12 日中 USDJPY 下跌 9 日(方向合套息平仓符号)、上涨 3 日;下跌日 USDJPY 累计 +0.17%、上涨日 +1.65%;四个最大下跌日 USDJPY 为 −0.07%/+0.20%/−0.08%/−0.06%。方向计数弱支持耦合、幅度可忽略,而窗内累计(SPX −5.51%、USDJPY +1.82%)与主解释预期相反——「尚不能区分」在逐日面站得住,建议补做入档。
  - 原句: 「竞争解释所需的『时间上解耦』须以逐日共动面核验，本档未做——尚不能区分。」
  - 改句(建议): 「可补入上述逐日共动数字(非必须)。」

- **NIT-2**
  - 位置: agent_judgment.json reader_map.turning_supplement[0].resolution_note
  - 问题: 「2026-08 的1.9,推定发布2026-08-30」按引擎规则(月末−1天)推得,该日为星期日;官方实录锚 2026-06-26、2026-10-30 均为星期五。结论(该读数早于 2026-09-18 决议发布)不受影响。
  - 原句: 「(当时可见的最近东京读数为 2026-08 的1.9,推定发布2026-08-30)」
  - 改句(建议): 「(当时可见的最近东京读数为 2026-08 的1.9,推定发布 2026-08-31 前后;规则值 2026-08-30 为星期日)」

- **NIT-3**
  - 位置: agent_judgment.json reader_map.regions[2].from_to(通胀)
  - 问题: 「最新4.0为四地最高通胀读数之一」: 就消费价格口径成立(HICP 4.0 高于日本 2.44、中国 0.7、美国最近有效同比 3.72@2026-09),但中国 PPI 同月为 5.7。「之一」为限定词,建议写明口径。
  - 原句: 「最新4.0为四地最高通胀读数之一」
  - 改句(建议): 「最新4.0为四地消费价格通胀的最高读数(中国PPI同月5.7为生产价格口径)」

- **NIT-4**
  - 位置: agent_judgment.json reader_map.regions[1].from_to(增长)
  - 问题: 制造业 PMI「同比口径 -2.2→-0.2→+0.61」为指数水平的同比百分比(回贴引擎格一致),非百分点;按百分点为 −1.10/−0.10/+0.30(49.0/49.2/49.3 对一年前 50.1/49.3/49.0)。易被读作百分点。
  - 原句: 「同比口径 -2.2→-0.2→+0.61」
  - 改句(建议): 「同比口径(指数水平同比%) -2.2%→-0.2%→+0.61%(约 −1.10/−0.10/+0.30 个百分点)」

- **NIT-5**
  - 位置: agent_judgment.json reader_map.turnings[1].first_mover
  - 问题: 「自1.7543折半至0.7972(2025-11→2026-02)」取引擎候选窗端点,「折半」成立(0.7972 < 1.7543/2);序列同比低点实为 2026-03 的 0.6861,比候选窗终点再低一个月。
  - 原句: 「美国工业生产同比自1.7543折半至0.7972(2025-11→2026-02)」
  - 改句(建议): 「美国工业生产同比自1.7543折半至0.7972(2025-11→2026-02,引擎候选窗端点;序列低点为 2026-03 的 0.69)」

- **NIT-6**
  - 位置: agent_judgment.json reader_map.regions[2].from_to(通胀)
  - 问题: 「2026-08至10加速」: 三个月增量 +0.30/+0.60/+0.20,均高于 2026-07 的 +0.10,但非逐月递增。措辞可更精确。
  - 原句: 「自2026-07再度上行(2026-08至10加速)」
  - 改句(建议): 「自2026-07再度上行(2026-08至10月度增量 +0.30/+0.60/+0.20,均高于7月的 +0.10)」

- **NIT-7**
  - 位置: agent_judgment.json reader_map.turnings[0].first_mover;turnings[1].first_mover
  - 问题: 关系词「最大」的口径: 「通胀维最大转折=美国CPI」在括注中限定为「候选面最大美欧值」(引擎通胀维候选首位为中国PPI,+4.8 对美国CPI +1.73);「增长维最大单指标转折=美国工业」而引擎增长维候选首位为中国制造业PMI(判断档写作「z口径 -2.3904→1.0101」,引擎候选面单位为「同比%(派生于水平序列,严格同基期)」、增量 3.40;质量注记[5]-⑤已把该栏名登记为渲染层文案),同条已说明未单列的理由。引导词宜与括注口径一致。
  - 原句: 「通胀维最大转折=美国CPI同比自2.434升至4.1666(2026-02→2026-05,3个月滚动窗候选面最大美欧值)」
  - 改句(建议): 「通胀维美欧最大转折=美国CPI同比自2.434升至4.1666(2026-02→2026-05,3个月滚动窗候选面最大美欧值);turnings[1] 同理写作「增长维美欧最大单指标转折=美国工业生产同比…(候选面全体首位为中国制造业PMI,增量3.40)」」

- **NIT-8**
  - 位置: agent_judgment.json quality_gate_notes[3]
  - 问题: 「证据引用共 41 条」为 L3 的引用条数;L4 两情景另有 9 条,合计 50 条,去重 20 个序列@日期。范围未注明。
  - 原句: 「证据引用共 41 条，全部取自本轮冻结快照 research_snapshot_20261123。」
  - 改句(建议): 「L3 证据引用共 41 条(连同 L4 共 50 条、去重 20 项),全部取自本轮冻结快照 research_snapshot_20261123。」

- **NIT-9**
  - 位置: agent_judgment.json reader_map.regions[0].from_to(增长维,12个月前锚)
  - 问题: 美国 12 个月前锚的 GDP 观测为 2025Q2(2025-04),欧元区、日本同锚为 2025Q3(2025-07): 冻结日历条目 RC-2025SHUTDOWN-GDP-Q3 载 2025Q3 GDP 因 2025 年联邦政府停摆延至 2025-12-23 首发,锚日 2025-11-23 不可见,取值正确。但三地「12个月前」增长读数的统计期相差一季,判断档未说明;读者报告的发布面表已载该延误。
  - 原句: 「增长: 实际GDP同比 2.42→2.19→2.07(观测 2025-04→2026-04→2026-07,水平 23884.563→24408.011→24611.077 十亿美元,即2025Q2→2026Q2→2026Q3)温和放缓」
  - 改句(建议): 「增长: 实际GDP同比 2.42→2.19→2.07(观测 2025-04→2026-04→2026-07,水平 23884.563→24408.011→24611.077 十亿美元,即2025Q2→2026Q2→2026Q3;12个月前锚只见2025Q2——2025Q3 GDP因2025年政府停摆延至2025-12-23首发,冻结日历实录,较欧元区、日本同锚早一季)温和放缓」

- **NIT-10**
  - 位置: agent_judgment.json reader_map.transmission[0].links[1].observed_fact(推定发布日)
  - 问题: 两处美国 CPI 推定发布日按引擎规则(月末+13 天)推得,却落在周末: 2026-05 观测「推定发布 2026-06-13」为星期六,2026-08 观测「推定发布 2026-09-13」为星期日(冻结日历无该两月 CPI 实录条目);两处均已标「推定」。结论对发布日不敏感: 2026-08 观测的推定日期早于 2026-09-16/2026-09-18 两次决议且留有 3 天余量;2026-05 观测若实际早于 2026-06-11 发布,欧央行首次决议前最近可见即为高点 4.17,「仍处上行段」的表述不变。
  - 原句: 「2026-05 高点 4.17(推定发布 2026-06-13)」
  - 改句(建议): 「2026-05 高点 4.17(推定发布 2026-06-13 前后;规则值为星期六)」

- **NIT-11**
  - 位置: agent_judgment.json l4.scenarios[1].rows.falsification.threshold
  - 问题: 反例情景的证伪阈值 1.8 未说明取值依据: 截止日 BEI_10Y 读数 2.15@2026-11-20,距阈值 35 个基点;库内最近一次低于 1.8 为 2020-11-30(1.77),近 24 个观测无一触及。阈值可观测(指标在库、历史上到过该水平),不属『不可观测』,但在 2027-02-28 期限内偏难触发,属阈值松紧未披露。
  - 原句: 「BEI_10Y 跌破1.8且继续下行——盈亏平衡通胀不回升反深跌,『一次性通胀+宽松预期修复』前提失效(深跌 BEI 指向衰退定价而非修复)」
  - 改句(建议): 「BEI_10Y 跌破1.8且继续下行(阈值依据: 库内最近一次低于 1.8 为 2020-11-30,较截止日读数 2.15 低 35 个基点,作深跌确认线)——盈亏平衡通胀不回升反深跌,『一次性通胀+宽松预期修复』前提失效(深跌 BEI 指向衰退定价而非修复)」

## 7. 引擎面与渲染面旁注(不计入问题清单)

以下为本席在只读面上看到、但不属于受审判断文字的问题或口径说明,供操作席与引擎侧参考:

1. 转折候选面是跨单位按 Δ 绝对值排序后截取的前 9 项(report.json candidates 共 9 项,研判席工单 turning_candidates_top9=9),Δ 由四位小数端点相减而得;渲染面内没有政策维行。本席对政策维序列做同规则扫描(仅作信息,见 info_candidates_ledger.txt): JP_POLICY_RATE 0.727→0.978 即 +0.251、DFEDTARU 4.0→3.75 与 DFF 3.89→3.64 即 −0.25,均小于候选面第 9 名(CORE_CPI 的 0.3767)——这与「政策维不在前 9 项内」相容,但引擎是否把政策维序列纳入候选池,本席未在只读面上核实。政策维事件经研判席工单的 policy_event_clusters 面进入,判断档的走位与传导链政策环已覆盖。
2. 判断档 quality_gate_notes 六条(证据与口径、对质面、证伪面、数据面、政策口径披露、引擎缺口披露)与 agent_declaration 原文只存于 agent_judgment.json,未渲染进 MAP_REPORT.md、FULL_REPORT.md 与 report.md。
3. MAP_REPORT.md 正文没有 Gate A 状态行(「Gate A」字样 0 处),数据面降级只在判断档披露。
4. S5 相关系数(栏名与口径不符,建议引擎侧更正): report.json steps[60] 的 pearson_returns=−0.8936(n=37 对)在 FULL_REPORT.md 与 report.md 渲染于「日度相关」标题下,写作「US_REAL_GDP×UNEMPLOYMENT 日收益×日变化」。本席自冻结快照逐位复现该值(差值小于 1e-9,见 info_s5_repro.txt): 它是季频 GDP 水平在相邻季初观测之间的百分比变化与失业率在同一对月份之间的百分点变化的相关系数(引擎面自述 month_grid 对齐、change_basis a=pct/b=pp、两侧频率 quarterly vs monthly),并非日收益;数值本身与证据面一致,错在栏名。MAP_REPORT.md 未渲染该行,判断档未引用,故不计入问题清单。
5. CN_PPI_YOY、CN_CPI_YOY 的证据引用标签日为观测月末(2026-10-31),序列观测日为月初(2026-10-01);判断档已自行披露。
6. 转折表「z口径」栏显示的是制造业PMI指数的同比百分数(−2.3904→1.0101),栏名容易误读为标准化分数;判断档已披露为渲染层文案。
7. 引擎「政策一年窗路径」面板按窗内首观测→窗末观测计净变动(日本 +67bp、欧央行两利率各 +25bp),对按步跳变、两次调整之间保持不变的序列漏计窗启时在值的升幅(按「窗启时在值→窗末」口径为 +75/+50/+50bp);判断档 quality_gate_notes[4] 已披露该口径差,正文采用后者并保留面板值,本席两口径均复算一致。
8. 欧央行利率序列止于 2026-09-16(滞后 68 天),中国政策利率新锚(隔夜逆回购利率)2026-11-02 起才有观测,NIKKEI225 止于 2026-11-20——判断档均已披露;SCN2 的「下一次决议」在截止日之后,属待观测。
9. 判断档自行标注的美国 CPI 与东京 CPI「推定发布日」是研判席按惯例的推定,冻结日历无对应条目;其中三处落在周末(NIT-2、NIT-10)。
10. 本席脚本 s38_policy_dates.py 首跑有 2 处席位自身缺陷(欧央行决议日回推方向、缺席的表示法),经脚本自检发现后修正并自备份重跑;s40_add_c2_rows.py 首跑因台账值存四位小数而对账容差设得过严,在写盘前即中止,修正后重跑。台账只保留重跑后的结果。

## 8. 文件索引(均在 /tmp/r32-accept/review3/A_round1/)

| 文件 | 用途 |
|---|---|
| _protocol.md | 席位规程 |
| VERDICT-round1.json | 裁决档(规程第 6 节结构) |
| PROSE-round1.md | 本文件(由 s35_build_prose.py 拼装) |
| points_all.jsonl | 逐点台账(1049 行: 计点 1006、信息 43) |
| s10_recompute.py | 主体复算(锚点、月频、日频、历史段、交付门、契约) |
| s20_checks.py、s21_rates_horizon.py、s22_decl_checks.py | 六查素材、利率分解各窗、声明与契约核对 |
| s24_engine_sync.py、s24a_find_sync.py、s24_sync_labels.py | 引擎同步面读取与标签比对 |
| s25_check_originals.py | 裁决档原句逐字回查判断档与读者报告 |
| s26_compare_face.py、s27_render_consistency.py、s28_render_check.py、s29_notes_fix.py、s29c_counts_fix.py | 引擎面比对、渲染一致性、裁决档修订 |
| s30a–s30f | 台账画像与检索工具 |
| s30g_snap_facts.py、s30h_refs_index.py、s30i_candidates.py | 快照单点事实、证据引用回查、候选面初查 |
| s31a_add_nit10.py | 追加 NIT-10 |
| s32_add_candidates.py | 追加转折候选面 40 行 |
| s33_envelope_pool.py | 研判席工单结构读取 |
| s34_update_verdict_counts.py、s34b_add_refs.py、s34c_add_nit11.py、s39_refresh_counts.py | 裁决档计数与条目更新、证据引用 20 行、NIT-11、政策面计数 |
| s35_build_prose.py | 拼装本文件 |
| s36_ledger_types.py | 台账类型画像(核对本文件 0.4 节的表述) |
| s37_threshold_history.py | 证伪阈值的可观测性与历史触及情况 |
| s38_policy_dates.py | 追加政策面 32 计点行与 1 信息行 |
| s40_add_c2_rows.py | 追加 C2 陈述事后方向归纳 4 行并刷新裁决档计数 |
| s41_disclose_dups.py | 在裁决档 notes 内补写重复记录说明(不改台账与计数) |
| s42_decision_cpi.py → info_decision_cpi.txt | 各决议日前可见的本地区通胀读数(只读计算) |
| s43_s5_repro.py → info_s5_repro.txt | S5 相关系数的口径复现(只读计算) |
| s31_check_outputs.py | 产出文件终检(JSON 结构、计数、原句、占位符) |
| prose_head.md、prose_tail.md | 本文件的固定文字部分(台账表由脚本填入) |
| info_*.txt、*_dump.txt、*_dump.json、*_table.txt | 各脚本的只读输出与中间表 |
| points_all.before-*.jsonl、VERDICT-round1.before-*.json | 追加或修订前的备份 |
