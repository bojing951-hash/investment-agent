# 语义审查复算记录 — Audit-R32 正式使用验收 · A 问 · Round-1

| 项 | 内容 |
|---|---|
| 席位 | semantic-audit-seat(零上下文独立席) |
| 审查者标识 | independent-zero-context-seat-r32-a-round1 |
| 审查日期 | 2026-11-24 |
| 受审对象 | 受审运行目录(20261123T145753Z_…)内 agent_judgment.json 全文(agent_declaration、l3、l4、reader_map、quality_gate_notes)与 MAP_REPORT.md 中的判断文字 |
| 代码印章(规程第 0 节披露,本席未核对) | 19638e1487e1e5729b9645ce621c3435d0635d08 |
| 裁决 | **UPHELD** — MAJOR 0 / MINOR 9 / NIT 11;must_fix 为空 |
| 复算计点 / 偏离 | {{COUNTS}} |

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

> {{NOTES}}

## 1. 复算清单

### 1.1 分节计数

{{SUMMARY_TABLE}}

### 1.2 逐点台账(出处键 / 直算值 / 报告值 / 一致与否)

{{POINTS}}
