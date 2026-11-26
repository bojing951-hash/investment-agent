# Audit-R32 · T3 · Round-1 · 独立语义审查席复算记录

- 审查席: semantic-audit-seat;reviewer: independent-zero-context-seat-r32-t3-round1;audited_at: 2026-11-24
- 裁决: **UPHELD**(MAJOR 0 / MINOR 7 / NIT 9);范围内复算 396 点,命中 396,偏离 0。
- 本记录只依据本席在只读面上亲自复算到的东西;未读取任何既有评审内容,未与研判席或操作者通信。

## 0. 审查对象、只读面与方法

- 问句原文: 「2026年11月,日本和欧元区的通胀与政策环境:两地央行当前官方政策目标利率各处于什么水平?最近六个月有无已决议但尚未生效的调整?两地通胀同比最新读数相比去年同月如何?请给出具体数据和各数据的公布时间。」
- 受审运行目录(只读): `/tmp/r32-accept/final5/output/research_runs/20261123T213336Z_2026年11月_日本和欧元区的通胀与政策环境_两地央行当前官方政策目标利率各处`
- 隔离安装树(只读): `/tmp/r32-accept/final5`
- 代码印章: report.json run.git_head 与 CODE_VERSION git_head 均为 `8f9055d6e556700b08f28a3abeff284cf0c8d71f`(A012)。
- 冻结输入印章(sha256 前 16 位): release_calendar `e44fd2aa5ced0310`、metric_registry `fa396d22175a4814`、snapshot `2d650f1128cdd356`;运行目录 overlay 副本、report.json run.frozen_inputs 与协议印章一致(A013–A015);MAP_REPORT.md 的 sha256 与 MAP_REPORT.sha256 一致(A016)。
- 本席成文时复算(运行目录 root_overlay 三件冻结输入,sha256 前 16 位): release_calendar `e44fd2aa5ced0310`, metric_registry `fa396d22175a4814`, snapshot `2d650f1128cdd356`;MAP_REPORT.md 全 64 位 `4648912e2d368e2cafe16313832b09002cdfe00bbebf2f01e43866c0164ce2e0`。
- 约束遵守: 未联网;未运行 ia_cli 的任何写操作;未调用裁决登记;未写入/移动/删除受审目录与安装树内任何文件;未读取规程第 2 节所列目录;未委派子代理。
- 方法: 全部复算由 `/usr/bin/python3 -I <脚本> <路径参数…>` 完成,路径一律作参数传入,脚本与产出只写本目录。一条复算点判「一致」须同时满足: 直算值按报告自身小数位四舍五入后等于报告值,且(若给出字面)该字面在判断档对应文本中逐字在场。
- 脚本: s10_common.py(公共读函数与台账);s11(①–⑥)/s12(⑦–⑩)/s14(⑪–⑮)/s18、s24(数字覆盖清查补点)为复算脚本;s20_counter.py 为反方攻击复算;s25_supplement.py 为本席自有发现的补充计算;s16 两份为数字覆盖清查;s15_merge.py 合并出 recompute_points.json 与 recompute_table.md;s27/s28 为成文前的引用核对探针;s30/s34/s35 为注册表文字与判断档原文的核对探针;s31 为成稿浏览;s32 为问题清单 where 路径核对(每条问题的原句须在其所引位置逐字在场);s29 为产出校验(裁决档结构、敏感字扫描);s23 生成本记录与裁决档。中间表: recompute_points_A–E.json、recompute_points.json、recompute_table.md、counterexamples.json、supplement.json。
- 行号约定: A=①,B=②,C=③,D=④,E=⑤,F=⑥,G=⑦,H=⑧,I=⑨,J=⑩,K=⑪,L=⑫,M=⑬,N=⑭,O=⑮;D1xx/D2xx=数字覆盖清查补点,CN=三条矛盾陈述内中文数字的逐句直算。

## 1. 复算清单

### 1.1 按类别小计

| 类别 | 范围 | 计入点数 | 命中 | 偏离 | 重复复核 | 范围外观察 |
|---|---|---|---|---|---|---|
| ① | 研究截止日/印章/推定发布日 | 26 | 26 | 0 | 0 | 0 |
| ② | 点值锚格(六个月前/最新一期) | 36 | 36 | 0 | 0 | 0 |
| ③ | 同比(基期/差值/方向词) | 18 | 18 | 0 | 0 | 0 |
| ④ | 政策面(变更点/生效日/决议日/目标值) | 42 | 42 | 0 | 0 | 0 |
| ⑤ | 三利率分解与资产月窗回贴 | 19 | 19 | 0 | 0 | 0 |
| ⑥ | 转折判断与候选面 | 40 | 40 | 0 | 0 | 0 |
| ⑦ | 传导链各环(E1/E2)与对质三环 | 104 | 104 | 0 | 0 | 0 |
| ⑧ | 历史类比 | 7 | 7 | 0 | 0 | 0 |
| ⑨ | 情景(证伪/触发/时限) | 17 | 17 | 0 | 0 | 0 |
| ⑩ | 总判断/走位/对质表一致性 | 23 | 23 | 0 | 0 | 3 |
| ⑪ | 诚实缺席项 | 14 | 14 | 0 | 0 | 1 |
| ⑫ | 截止日当日日频观测时点 | 9 | 9 | 0 | 0 | 0 |
| ⑬ | 契约验证非 VERIFIED 项(STALE)披露 | 5 | 5 | 0 | 0 | 0 |
| ⑭ | 交付门相关缺口披露 | 11 | 11 | 0 | 0 | 0 |
| ⑮ | 目标利率数值/生效日/现行有效/待生效分记、同比基期 | 13 | 13 | 0 | 0 | 1 |
| 补 | 数字覆盖清查(逐对/逐句复核后新增的点) | 12 | 12 | 0 | 72 | 0 |
| **合计** | | **396** | **396** | **0** | 72 | 5 |

说明: 「重复复核」指本席为数字覆盖清查又做了一遍、但与已计点同指标同时点同值的复核(72 条全中),不重复计入点数;「范围外观察」是引擎渲染或引擎口径面的不一致(复算值与引擎面值不同,但不是判断档的偏离),单列于第 5 节,不计入命中/偏离。

### 1.2 数字覆盖清查

- 判断档承载判断的文字(三条矛盾陈述及其竞争解释、机制链四环、总判断、两地走位、对质三环全部字段、三转折、情景、质量门注记)内阿拉伯数字 478 个词元: 未覆盖 0。其中注册表拼接告警阈 0.10pp 与汇市单日变动上限 0.23% 两类词元由专门行判定(D204、D201),其余按数值或年月与某条一致行的直算值相等。
- 三条矛盾陈述内中文数字 36 个词元: 35 个对应到直算行的字面(CN001–CN017 及 C/D 类各行),余 1 个为序数词「一次」(「最近一次变更日」),非量值。
- 说明: 这一步是「每个数字都有出处」的兜底,不替代逐类复算;清查中新增并计入的点共 12 个(D 类 7、CN 类 5)。

### 1.3 逐点清单

| 序 | 编号 | 类别 | 位置 | 出处键 | 直算值 | 报告值 | 一致 | 备注 |
|---|---|---|---|---|---|---|---|---|
| 1 | A001 | ① | 研究截止日 | snapshot.target_date / report.json:research_plan.cutoff | 2026-11-23 | 2026-11-23 | 是 | 字面命中 |
| 2 | A002 | ① | 证据截止 | report.json:run.evidence_asof vs research_plan.cutoff | 2026-11-23 | 2026-11-23 | 是 | 字面命中 |
| 3 | A003 | ① | 快照时间戳 | snapshot.research_as_of | 2026-11-23T22:53:47+08:00 | 2026-11-23T22:53:47+08:00 | 是 | 字面命中 |
| 4 | A004 | ① | 快照时间戳时区换算 | snapshot.research_as_of -> NewYork 本地时间 | 09:53 | 09:53 | 是 | 字面命中 |
| 5 | A005 | ① | 快照时间戳时区换算 | snapshot.research_as_of -> Berlin 本地时间 | 15:53 | 15:53 | 是 | 字面命中 |
| 6 | A006 | ① | 快照时间戳时区换算 | snapshot.research_as_of -> Tokyo 本地时间 | 23:53 | 23:53 | 是 | 字面命中 |
| 7 | A007 | ① | 快照时间戳时区换算 | snapshot.research_as_of -> Shanghai 本地时间 | 22:53 | 22:53 | 是 | 字面命中 |
| 8 | A008 | ① | 晚于截止日的日期字面 | agent_judgment.json 全文正则扫描+逐处路径归类 | {"2026-11-24": [".agent_declaration.written_at"], "2027-02-15": [".l4.… | 仅成文时间戳(agent_declaration.written_at)或情景时限(l4.scenarios 与 quality_gate_… | 是 | 2026-11-24 仅为成文时间戳(written_at); 2027-02-15 仅为情景时限 |
| 9 | A009 | ① | 晚于截止月的月份字面 | agent_judgment.json 全文正则扫描+逐处路径归类 | {"2026-12": [".l4.scenarios[0].rows.falsification.threshold", ".l4.sce… | 仅情景观测月/入档月(l4.scenarios) | 是 | 截止月后月份须仅出现在情景层(前瞻标注【假设·非预测】) |
| 10 | A010 | ① | 最近六个月窗口 | cutoff-6月 vs judgment | 2026-05-23 | 2026-05-23 | 是 | 字面命中 |
| 11 | A011 | ① | 引擎窗口端点 | report.json:research_plan.question_window | 2026-05-23..2026-11-23 | 2026-05-23..2026-11-23 | 是 |  |
| 12 | A012 | ① | 代码印章 | report.json:run.git_head / CODE_VERSION.json:git_head | true | true | 是 | 8f9055d6e556 |
| 13 | A013 | ① | 冻结输入哈希 | sha256(config/release_calendar.json) 前16位 vs report.json:run.frozen_inputs | e44fd2aa5ced0310 | e44fd2aa5ced0310 | 是 | 运行目录 overlay 副本=e44fd2aa5ced0310, 协议印章=e44fd2aa5ced0310, 三者一致 |
| 14 | A014 | ① | 冻结输入哈希 | sha256(config/metric_registry.json) 前16位 vs report.json:run.frozen_inputs | fa396d22175a4814 | fa396d22175a4814 | 是 | 运行目录 overlay 副本=fa396d22175a4814, 协议印章=fa396d22175a4814, 三者一致 |
| 15 | A015 | ① | 冻结输入哈希 | sha256(data/daily/research_snapshot_20261123.json) 前16位 vs report.json:run.frozen_inputs | 2d650f1128cdd356 | 2d650f1128cdd356 | 是 | 运行目录 overlay 副本=2d650f1128cdd356, 协议印章=2d650f1128cdd356, 三者一致 |
| 16 | A016 | ① | 读者报告校验 | MAP_REPORT.sha256 vs sha256(MAP_REPORT.md) | 4648912e2d368e2cafe16313832b09002cdfe00bbebf2f01e43866c0164ce2e0 | 4648912e2d368e2cafe16313832b09002cdfe00bbebf2f01e43866c0164ce2e0 | 是 |  |
| 17 | A017 | ① | 发布日(推定规则) | research_snapshot_20261123.json:series_store 月末+20天 vs point_values.publication_date | 2026-11-20 | 2026-11-20 | 是 | 字面命中 |
| 18 | A018 | ① | 发布日(推定规则) | research_snapshot_20261123.json:series_store 月末+16天 vs point_values.publication_date | 2026-11-16 | 2026-11-16 | 是 | 字面命中 |
| 19 | A019 | ① | 发布日(推定规则) | research_snapshot_20261123.json:series_store 月末-1天 vs point_values.publication_date | 2026-10-30 | 2026-10-30 | 是 | 字面命中 |
| 20 | A020 | ① | 发布日(推定规则) | JP_POLICY_RATE 月末+5天 vs point_values.publication_date | 2026-11-05 | 2026-11-05 | 是 | 判断档正文未给出 JP_POLICY_RATE 的发布日(仅观测月) |
| 21 | A021 | ① | 六个月前锚可见性 | research_snapshot_20261123.json:series_store + 推定规则: 发布日≤2026-05-23 的最新观测月; 次月发布日=2026-06-… | 2026-04 | 2026-04 | 是 |  |
| 22 | A022 | ① | 六个月前锚可见性 | research_snapshot_20261123.json:series_store + 推定规则: 发布日≤2026-05-23 的最新观测月; 次月发布日=2026-06-… | 2026-04 | 2026-04 | 是 |  |
| 23 | A023 | ① | 六个月前锚可见性 | research_snapshot_20261123.json:series_store + 推定规则: 发布日≤2026-05-23 的最新观测月; 次月发布日=2026-05-… | 2026-04 | 2026-04 | 是 |  |
| 24 | A024 | ① | 六个月前锚可见性 | research_snapshot_20261123.json:series_store + 推定规则: 发布日≤2026-05-23 的最新观测月; 次月发布日=2026-06-… | 2026-04 | 2026-04 | 是 |  |
| 25 | A025 | ① | 日历优先/无实录 | release_calendar.json:entries 命中检索 | [] | [] | 是 | 字面命中;命中空集=只能用推定规则 |
| 26 | A026 | ① | EA HICP 日历实录形态 | release_calendar.json:entries EA_HICP_YOY(3 条): 快报日=次月首日 且 有终值日 | [3, true] | [3, true] | 是 | 字面命中;实录: RC-EA-HICP-2021M05 快报 2021-06-01/终值 2021-06-17; RC-EA-HICP-2022M06 快报 2022-07-01/终值 20… |
| 27 | B001 | ② | EA 走位/点值格 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-04]+推定规则(发布日≤2026-05-23) | 3.0 | 3.0 | 是 | 字面命中 |
| 28 | B002 | ② | EA 点值格 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-04]+推定规则(发布日≤2026-05-23) 观测日 | 2026-04-01 | 2026-04-01 | 是 |  |
| 29 | B003 | ② | EA anchor_echo | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-04]+推定规则(发布日≤2026-05-23) | [3.0, "2026-04"] | [3.0, "2026-04"] | 是 | 字面命中 |
| 30 | B004 | ② | EA 走位/点值格 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10]+推定规则(发布日≤2026-11-23) | 4.0 | 4.0 | 是 | 字面命中 |
| 31 | B005 | ② | EA 点值格 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10]+推定规则(发布日≤2026-11-23) 观测日 | 2026-10-01 | 2026-10-01 | 是 |  |
| 32 | B006 | ② | EA anchor_echo | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10]+推定规则(发布日≤2026-11-23) | [4.0, "2026-10"] | [4.0, "2026-10"] | 是 | 字面命中 |
| 33 | B007 | ② | EA 走位/点值格 | research_snapshot_20261123.json:series_store.ECB_MRO 发布日≤2026-05-23 的最后观测 | 2.15 | 2.15 | 是 | 字面命中 |
| 34 | B008 | ② | EA 点值格 | research_snapshot_20261123.json:series_store.ECB_MRO 发布日≤2026-05-23 的最后观测 观测日 | 2025-06-11 | 2025-06-11 | 是 |  |
| 35 | B009 | ② | EA anchor_echo | research_snapshot_20261123.json:series_store.ECB_MRO 发布日≤2026-05-23 的最后观测 | [2.15, "2025-06"] | [2.15, "2025-06"] | 是 | 字面命中 |
| 36 | B010 | ② | EA 走位/点值格 | research_snapshot_20261123.json:series_store.ECB_MRO 发布日≤2026-11-23 的最后观测 | 2.65 | 2.65 | 是 | 字面命中 |
| 37 | B011 | ② | EA 点值格 | research_snapshot_20261123.json:series_store.ECB_MRO 发布日≤2026-11-23 的最后观测 观测日 | 2026-09-16 | 2026-09-16 | 是 |  |
| 38 | B012 | ② | EA anchor_echo | research_snapshot_20261123.json:series_store.ECB_MRO 发布日≤2026-11-23 的最后观测 | [2.65, "2026-09"] | [2.65, "2026-09"] | 是 | 字面命中 |
| 39 | B013 | ② | EA 走位/点值格 | research_snapshot_20261123.json:series_store.ECB_DFR 发布日≤2026-05-23 的最后观测 | 2.0 | 2.0 | 是 | 字面命中 |
| 40 | B014 | ② | EA 点值格 | research_snapshot_20261123.json:series_store.ECB_DFR 发布日≤2026-05-23 的最后观测 观测日 | 2025-06-11 | 2025-06-11 | 是 |  |
| 41 | B015 | ② | EA anchor_echo | research_snapshot_20261123.json:series_store.ECB_DFR 发布日≤2026-05-23 的最后观测 | [2.0, "2025-06"] | [2.0, "2025-06"] | 是 | 字面命中 |
| 42 | B016 | ② | EA 走位/点值格 | research_snapshot_20261123.json:series_store.ECB_DFR 发布日≤2026-11-23 的最后观测 | 2.5 | 2.5 | 是 | 字面命中 |
| 43 | B017 | ② | EA 点值格 | research_snapshot_20261123.json:series_store.ECB_DFR 发布日≤2026-11-23 的最后观测 观测日 | 2026-09-16 | 2026-09-16 | 是 |  |
| 44 | B018 | ② | EA anchor_echo | research_snapshot_20261123.json:series_store.ECB_DFR 发布日≤2026-11-23 的最后观测 | [2.5, "2026-09"] | [2.5, "2026-09"] | 是 | 字面命中 |
| 45 | B019 | ② | JP 走位/点值格 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-04]+推定规则(发布日≤2026-05-23) | 1.38 | 1.38 | 是 | 字面命中 |
| 46 | B020 | ② | JP 点值格 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-04]+推定规则(发布日≤2026-05-23) 观测日 | 2026-04-01 | 2026-04-01 | 是 |  |
| 47 | B021 | ② | JP anchor_echo | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-04]+推定规则(发布日≤2026-05-23) | [1.38, "2026-04"] | [1.38, "2026-04"] | 是 | 字面命中 |
| 48 | B022 | ② | JP 走位/点值格 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-10]+推定规则(发布日≤2026-11-23) | 2.44 | 2.44 | 是 | 字面命中 |
| 49 | B023 | ② | JP 点值格 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-10]+推定规则(发布日≤2026-11-23) 观测日 | 2026-10-01 | 2026-10-01 | 是 |  |
| 50 | B024 | ② | JP anchor_echo | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-10]+推定规则(发布日≤2026-11-23) | [2.44, "2026-10"] | [2.44, "2026-10"] | 是 | 字面命中 |
| 51 | B025 | ② | JP 走位/点值格 | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2026-04]+推定规则(发布日≤2026-05-23… | 1.42 | 1.42 | 是 | 字面命中 |
| 52 | B026 | ② | JP 点值格 | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2026-04]+推定规则(发布日≤2026-05-23… | 2026-04-01 | 2026-04-01 | 是 |  |
| 53 | B027 | ② | JP anchor_echo | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2026-04]+推定规则(发布日≤2026-05-23… | [1.42, "2026-04"] | [1.42, "2026-04"] | 是 | 字面命中 |
| 54 | B028 | ② | JP 走位/点值格 | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2026-10]+推定规则(发布日≤2026-11-23… | 2.73 | 2.73 | 是 | 字面命中 |
| 55 | B029 | ② | JP 点值格 | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2026-10]+推定规则(发布日≤2026-11-23… | 2026-10-01 | 2026-10-01 | 是 |  |
| 56 | B030 | ② | JP anchor_echo | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2026-10]+推定规则(发布日≤2026-11-23… | [2.73, "2026-10"] | [2.73, "2026-10"] | 是 | 字面命中 |
| 57 | B031 | ② | JP 走位/点值格 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04]+推定规则(发布日≤2026-05-23) | 0.727 | 0.727 | 是 | 字面命中 |
| 58 | B032 | ② | JP 点值格 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04]+推定规则(发布日≤2026-05-23) … | 2026-04-01 | 2026-04-01 | 是 |  |
| 59 | B033 | ② | JP anchor_echo | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04]+推定规则(发布日≤2026-05-23) | [0.727, "2026-04"] | [0.727, "2026-04"] | 是 | 字面命中 |
| 60 | B034 | ② | JP 走位/点值格 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10]+推定规则(发布日≤2026-11-23) | 1.227 | 1.227 | 是 | 字面命中 |
| 61 | B035 | ② | JP 点值格 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10]+推定规则(发布日≤2026-11-23) … | 2026-10-01 | 2026-10-01 | 是 |  |
| 62 | B036 | ② | JP anchor_echo | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10]+推定规则(发布日≤2026-11-23) | [1.227, "2026-10"] | [1.227, "2026-10"] | 是 | 字面命中 |
| 63 | C001 | ③ | C1 去年同月基期 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2025-10-01] | 2.99 | 2.99 | 是 | 字面命中 |
| 64 | C002 | ③ | C1 同比读数差 | JP_CPI_YOY 2026-10 − 2025-10 | -0.55 | -0.55 | 是 | 字面命中 |
| 65 | C003 | ③ | C1 基期=同月(非相邻月) | research_snapshot_20261123.json:series_store.JP_CPI_YOY dates 含 2025-10-01 | true | true | 是 |  |
| 66 | C004 | ③ | C1 去年同月基期 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2025-10-01] | 2.1 | 2.1 | 是 | 字面命中 |
| 67 | C005 | ③ | C1 同比读数差 | EA_HICP_YOY 2026-10 − 2025-10 | 1.9 | 1.9 | 是 | 字面命中 |
| 68 | C006 | ③ | C1 基期=同月(非相邻月) | research_snapshot_20261123.json:series_store.EA_HICP_YOY dates 含 2025-10-01 | true | true | 是 |  |
| 69 | C007 | ③ | C1 东京基期缺席 | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY[2025-10-01] | null | null | 是 | 字面命中 |
| 70 | C008 | ③ | C1 东京序列起点 | research_snapshot_20261123.json:series_store.JP_CPI_TOKYO_YOY 首观测 | 2026-01-01 | 2026-01-01 | 是 | 字面命中 |
| 71 | C009 | ③ | 总判断 方向词 | JP_CPI_YOY 2026-10 < 2025-10 | true | true | 是 | 字面命中 |
| 72 | C010 | ③ | 总判断 方向词 | EA_HICP_YOY 2026-10 > 2025-10 | true | true | 是 | 字面命中 |
| 73 | C011 | ③ | 总判断 较六个月前锚 | JP_CPI_YOY/EA_HICP_YOY 2026-10 vs 2026-04 | true | true | 是 | 字面命中 |
| 74 | C012 | ③ | JP 走位 | JP_CPI_YOY 2025-10 − 2026-10 | 0.55 | 0.55 | 是 | 字面命中 |
| 75 | C013 | ③ | EA 走位 | EA_HICP_YOY 2026-10 − 2025-10 | 1.9 | 1.9 | 是 | 字面命中 |
| 76 | C014 | ③ | EA 走位 关系词 | EA_HICP_YOY 近十二个月(2025-11..2026-10)最大值 | ["2026-10", 4.0] | ["2026-10", 4.0] | 是 | 字面命中 |
| 77 | C015 | ③ | EA 走位 谷底 | EA_HICP_YOY 近十二个月最小值 | ["2026-01", 1.7] | ["2026-01", 1.7] | 是 | 字面命中 |
| 78 | C016 | ③ | JP 走位 谷底 | JP_CPI_YOY 近十二个月最小值 | ["2026-02", 1.27] | ["2026-02", 1.27] | 是 | 字面命中 |
| 79 | C017 | ③ | JP 同比口径 | metric_registry.json:JP_CPI_YOY.calc | true | true | 是 | 字面命中 |
| 80 | C018 | ③ | EA 同比口径 | metric_registry.json:EA_HICP_YOY.calc 含『年度变化率』 | true | true | 是 | 字面命中 |
| 81 | D001 | ④ | C2 ECB_MRO 最后观测日 | research_snapshot_20261123.json:series_store.ECB_MRO[-1] | 2026-09-16 | 2026-09-16 | 是 | 字面命中 |
| 82 | D002 | ④ | C2 ECB_MRO 现行水平 | research_snapshot_20261123.json:series_store.ECB_MRO[2026-09-16] | 2.65 | 2.65 | 是 | 字面命中 |
| 83 | D003 | ④ | C2 ECB_DFR 现行水平 | research_snapshot_20261123.json:series_store.ECB_DFR[2026-09-16] | 2.5 | 2.5 | 是 | 字面命中 |
| 84 | D004 | ④ | C2 ECB_DFR 同日 | research_snapshot_20261123.json:series_store.ECB_DFR[-1] 日期 | 2026-09-16 | 2026-09-16 | 是 | 字面命中 |
| 85 | D005 | ④ | 政策变更点 | research_snapshot_20261123.json:series_store.ECB_MRO 变更点 2026-06-17 | ["2026-06-17", 2.15, 2.4, 25] | ["2026-06-17", 2.15, 2.4, 25] | 是 |  |
| 86 | D006 | ④ | 政策变更点 | research_snapshot_20261123.json:series_store.ECB_MRO 变更点 2026-09-16 | ["2026-09-16", 2.4, 2.65, 25] | ["2026-09-16", 2.4, 2.65, 25] | 是 |  |
| 87 | D007 | ④ | 政策变更点 | research_snapshot_20261123.json:series_store.ECB_DFR 变更点 2026-06-17 | ["2026-06-17", 2.0, 2.25, 25] | ["2026-06-17", 2.0, 2.25, 25] | 是 |  |
| 88 | D008 | ④ | 政策变更点 | research_snapshot_20261123.json:series_store.ECB_DFR 变更点 2026-09-16 | ["2026-09-16", 2.25, 2.5, 25] | ["2026-09-16", 2.25, 2.5, 25] | 是 |  |
| 89 | D009 | ④ | 生效日=周三 | weekday(2026-09-16) | Wed | Wed | 是 |  |
| 90 | D010 | ④ | 生效日=周三 | weekday(2026-06-17) | Wed | Wed | 是 |  |
| 91 | D011 | ④ | C2 决议日(回推) | 生效日前上一个周四(2026-09-16) | 2026-09-10 | 2026-09-10 | 是 | 字面命中 |
| 92 | D012 | ④ | C2 决议日(回推) | 生效日前上一个周四(2026-06-17) | 2026-06-11 | 2026-06-11 | 是 | 字面命中 |
| 93 | D013 | ④ | 传导环1 间隔 | 2026-09-16 − 2026-06-17 (天) | 91 | 91 | 是 | 字面命中 |
| 94 | D014 | ④ | C3 观测滞后 | cutoff − 2026-09-16 (天) | 68 | 68 | 是 | 字面命中 |
| 95 | D015 | ④ | C3 滞后(总判断) | cutoff − 2026-09-16 (天) | 68 | 68 | 是 | 字面命中 |
| 96 | D016 | ④ | C3 新鲜度阈 | metric_registry.json:ECB_MRO.freshness.max_calendar_lag_days | 10 | 10 | 是 | 字面命中;注册表同处另有 decision_dated 注记(无更晚已证实决议不作过期);引擎点值格 freshness_basis=policy_confirmation/status=o… |
| 97 | D017 | ④ | C3 Gate A | snapshot.gate_a.noncore_degraded 含 ECB_MRO/ECB_DFR | ["ECB_MRO", "ECB_DFR"] | ["ECB_MRO", "ECB_DFR"] | 是 | 字面命中 |
| 98 | D018 | ④ | C3 L1 质量 | report.json:L1 rows quality_status | ["DEGRADED", "DEGRADED"] | ["DEGRADED", "DEGRADED"] | 是 | 字面命中 |
| 99 | D019 | ④ | C3 日历无 ECB 实录 | release_calendar.json:entries | [] | [] | 是 | 字面命中 |
| 100 | D020 | ④ | C2 BOJ 决议日 | release_calendar.json:RC-JP-BOJ-TARGET-2026-09.decision_date | 2026-09-18 | 2026-09-18 | 是 | 字面命中 |
| 101 | D021 | ④ | C2 BOJ 生效日 | release_calendar.json:RC-JP-BOJ-TARGET-2026-09.effective_on | 2026-09-24 | 2026-09-24 | 是 | 字面命中 |
| 102 | D022 | ④ | C2 BOJ 目标值 | release_calendar.json:RC-JP-BOJ-TARGET-2026-09.target_value | 1.25 | 1.25 | 是 | 字面命中 |
| 103 | D023 | ④ | C2 BOJ 确认维持 | release_calendar.json:RC-JP-BOJ-MAINT-2026-10 | ["2026-10-30", 1.25, "policy_maintenance"] | ["2026-10-30", 1.25, "policy_maintenance"] | 是 | 字面命中 |
| 104 | D024 | ④ | C2 无待生效决定 | release_calendar.json 全部条目 effective_on > 截止日 计数 | [] | [] | 是 | 字面命中 |
| 105 | D025 | ④ | C2 维持后天数 | cutoff − 2026-10-30 (天) | 24 | 24 | 是 | 字面命中 |
| 106 | D026 | ④ | 读者报告 距上次调整 | cutoff − effective_on / decision_date / 维持日 (天) | 60天\|66天\|24天 | 60天\|66天\|24天 | 是 | 字面命中 |
| 107 | D027 | ④ | BOJ 首发日 | RC-JP-BOJ-TARGET-2026-09.first_publish_on_or_after | 2026-09-18 | 2026-09-18 | 是 |  |
| 108 | D028 | ④ | C2 窗内上调次数 | ECB_MRO 变更点落在 [2026-05-23, 2026-11-23] | 2 | 2 | 是 | 字面命中 |
| 109 | D029 | ④ | JP 走位 目标口径缺席 | metric_registry.json:metrics 含 JP_POLICY_TARGET | false | false | 是 | 字面命中 |
| 110 | D030 | ④ | C2 月均≠宣布值 | metric_registry.json:JP_POLICY_RATE.calc | true | true | 是 | 字面命中 |
| 111 | D031 | ④ | 传导环2 联邦基金目标区间 | research_snapshot_20261123.json:series_store.DFEDTARL/DFEDTARU[2026-11-23] | [3.75, 4.0] | [3.75, 4.0] | 是 | 字面命中 |
| 112 | D032 | ④ | 传导环2 美联储生效日 | research_snapshot_20261123.json:series_store.DFEDTARU 最后变更点 | 2026-09-17 | 2026-09-17 | 是 | 字面命中 |
| 113 | D033 | ④ | 传导环2 索引外引用披露 | report.json:evidence_index 含 DFEDTARL/U | [] | [] | 是 | 字面命中 |
| 114 | D034 | ④ | JP 走位 近12月净变动 | JP_POLICY_RATE 2026-10 − 2025-11 (bp) | 75.0 | 75 | 是 | 字面命中 |
| 115 | D035 | ④ | JP 走位 变动点之和 | JP_POLICY_RATE 窗内(>2025-11-23)变动点 bp 之和 | 75 | 75 | 是 | 字面命中 |
| 116 | D036 | ④ | JP 走位 变动点个数 | 同上 变动点个数 | 6 | 6 | 是 |  |
| 117 | D037 | ④ | JP 走位 一年窗 | research_plan.point_values.JP_POLICY_RATE.policy_window_path.window | 2025-11-23..2026-11-23 | 2025-11-23..2026-11-23 | 是 | 字面命中 |
| 118 | D038 | ④ | M1-2 月均台阶 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE 2026-09/2026-10 | [1.043, 1.227] | [1.043, 1.227] | 是 | 字面命中 |
| 119 | D039 | ④ | C2 月均锚 | JP_POLICY_RATE 2026-04 / 2026-10 | [0.727, 1.227] | [0.727, 1.227] | 是 | 字面命中 |
| 120 | D040 | ④ | C2 月均起点 | JP_POLICY_RATE 2025-11 | 0.478 | 0.478 | 是 | 字面命中 |
| 121 | D041 | ④ | 读者报告 一年窗净变动闭合 | ECB_MRO policy_window_path 净变动 vs 变动点之和 vs 序列首尾差 | [50, 50, 50] | [50, 50, 50] | 是 |  |
| 122 | D042 | ④ | 读者报告 一年窗净变动闭合 | ECB_DFR policy_window_path 净变动 vs 变动点之和 vs 序列首尾差 | [50, 50, 50] | [50, 50, 50] | 是 |  |
| 123 | E001 | ⑤ | rates_decomposition 名义 | research_snapshot_20261123.json:series_store.UST_10Y 2026-10-20→2026-11-19 (bp) (5.12→5.04… | -8.0 | -8.0 | 是 |  |
| 124 | E001b | ⑤ | rates_decomposition 名义(引擎面) | research_plan.us_rates_trio.chg_bp.UST_10Y vs reader_map | -8.0 | -8.0 | 是 |  |
| 125 | E002b | ⑤ | rates_decomposition 实际(引擎面) | us_rates_trio.chg_bp.TIPS_10Y vs reader_map | 11.0 | 11.0 | 是 |  |
| 126 | E003b | ⑤ | rates_decomposition 盈亏平衡(引擎面) | us_rates_trio.chg_bp.BEI_10Y vs reader_map | -19.0 | -19.0 | 是 |  |
| 127 | E002 | ⑤ | rates_decomposition 实际 | TIPS_10Y 2026-10-20→2026-11-19 (bp) (2.77→2.88) | 11.0 | 11.0 | 是 |  |
| 128 | E003 | ⑤ | rates_decomposition 盈亏平衡 | BEI_10Y 2026-10-20→2026-11-19 (bp) (2.35→2.16) | -19.0 | -19.0 | 是 |  |
| 129 | E004 | ⑤ | 名义=实际+盈亏平衡 | Δ名义 − (Δ实际+ΔBEI) 残差(bp) | -0.0 | 0.0 | 是 |  |
| 130 | E005 | ⑤ | 水平恒等 | 2026-11-19: UST_10Y − (TIPS_10Y+BEI_10Y) | 0.0 | 0.0 | 是 |  |
| 131 | E006 | ⑤ | rates_decomposition 窗起 | UST_10Y 2026-10-20 在场=三序列共同日 | 2026-10-20 | 2026-10-20 | 是 |  |
| 132 | E007 | ⑤ | rates_decomposition 窗止 | 三序列共同交易日最后一天 vs us_rates_trio.window.to(三序列各自最后观测 2026-11-19/2026-11-19/2026-11-20) | 2026-11-19 | 2026-11-19 | 是 | 引擎窗=共同交易日; BEI_10Y 单独另有 2026-11-20 观测(名义/实际无同日观测,不入共同窗) |
| 133 | E008 | ⑤ | 12个月窗 名义 | UST_10Y 2025-11-19→2026-11-19 (bp) | 91.0 | 91.0 | 是 |  |
| 134 | E009 | ⑤ | 12个月窗 实际 | TIPS_10Y 2025-11-19→2026-11-19 (bp) | 102.0 | 102.0 | 是 |  |
| 135 | E010 | ⑤ | 12个月窗 盈亏平衡 | BEI_10Y 2025-11-19→2026-11-19 (bp) | -11.0 | -11.0 | 是 |  |
| 136 | E011 | ⑤ | asset_returns_echo | research_snapshot_20261123.json:series_store.NIKKEI225 2026-10-23→2026-11-20 | -9.98 | -9.98 | 是 | 窗口 2026-10-23..2026-11-20(引擎 asset_moves 同窗) |
| 137 | E012 | ⑤ | asset_returns_echo | research_snapshot_20261123.json:series_store.DAX 2026-10-23→2026-11-23 | 0.11 | 0.11 | 是 | 窗口 2026-10-23..2026-11-23(引擎 asset_moves 同窗) |
| 138 | E013 | ⑤ | asset_returns_echo | research_snapshot_20261123.json:series_store.SPX 2026-10-23→2026-11-23 | -5.51 | -5.51 | 是 | 窗口 2026-10-23..2026-11-23(引擎 asset_moves 同窗) |
| 139 | E014 | ⑤ | asset_returns_echo | research_snapshot_20261123.json:series_store.VIX 2026-10-23→2026-11-23 | 38.87 | 38.87 | 是 | 窗口 2026-10-23..2026-11-23(引擎 asset_moves 同窗) |
| 140 | E015 | ⑤ | M1-4 VIX 盘中较收盘 | VIX 2026-11-23 vs 2026-11-20 | -24.74 | -24.7 | 是 | 字面命中 |
| 141 | E016 | ⑤ | M1-3 UST_10Y | UST_10Y 最后观测 | ["2026-11-19", 5.04] | ["2026-11-19", 5.04] | 是 | 字面命中 |
| 142 | F001 | ⑥ | 转折1 候选面同源 | research_plan.turning_candidates.candidates | [["2025-11", "2026-02", 2.9, 1.27]] | [["2025-11", "2026-02", 2.9, 1.27]] | 是 |  |
| 143 | F002 | ⑥ | 转折1 前值 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2025-11] | 2.9 | 2.9 | 是 |  |
| 144 | F003 | ⑥ | 转折1 后值 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-02] | 1.27 | 1.27 | 是 |  |
| 145 | F004 | ⑥ | 转折1 幅度 | 后值−前值 | -1.63 | -1.63 | 是 |  |
| 146 | F005 | ⑥ | 转折2 候选面同源 | research_plan.turning_candidates.candidates | [["2026-02", "2026-05", 1.9, 3.2]] | [["2026-02", "2026-05", 1.9, 3.2]] | 是 |  |
| 147 | F006 | ⑥ | 转折2 前值 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-02] | 1.9 | 1.9 | 是 |  |
| 148 | F007 | ⑥ | 转折2 后值 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-05] | 3.2 | 3.2 | 是 |  |
| 149 | F008 | ⑥ | 转折2 幅度 | 后值−前值 | 1.3 | 1.3 | 是 |  |
| 150 | F009 | ⑥ | 转折3 候选面同源 | research_plan.turning_candidates.candidates | [["2026-04", "2026-07", 0.727, 0.978]] | [["2026-04", "2026-07", 0.727, 0.978]] | 是 |  |
| 151 | F010 | ⑥ | 转折3 前值 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04] | 0.727 | 0.727 | 是 |  |
| 152 | F011 | ⑥ | 转折3 后值 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-07] | 0.978 | 0.978 | 是 |  |
| 153 | F012 | ⑥ | 转折3 幅度 | 后值−前值 | 0.251 | 0.251 | 是 |  |
| 154 | F013 | ⑥ | 转折1 关系词 | 候选池 \|delta\| 最大者 | JP_CPI_YOY@2026-02 | JP_CPI_YOY@2026-02 | 是 | 字面命中 |
| 155 | F014 | ⑥ | 转折1 首变 | JP_CPI_YOY 2025-11→2026-02 | [2.9, 1.27] | [2.9, 1.27] | 是 | 字面命中 |
| 156 | F015 | ⑥ | 转折1 同向 | EA_HICP_YOY 2025-11→2026-02 | [2.1, 1.9] | [2.1, 1.9] | 是 | 字面命中 |
| 157 | F016 | ⑥ | 转折1 谷底相邻 | 两序列近十二个月谷底月 | ["2026-01", "2026-02"] | ["2026-01", "2026-02"] | 是 | 字面命中 |
| 158 | F017 | ⑥ | 转折1 谷底月相差 | 谷底月差(月): 日本谷底月 − 欧元区谷底月 | 1 | 1 | 是 | 字面命中 |
| 159 | F018 | ⑥ | 转折1 候选面排序 | 候选面转折日(区间终点月) | ["2026-02", "2026-05"] | ["2026-02", "2026-05"] | 是 | 字面命中 |
| 160 | F019 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-03] | 1.46 | 1.46 | 是 | 字面命中 |
| 161 | F020 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-04] | 1.38 | 1.38 | 是 | 字面命中 |
| 162 | F021 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-05] | 1.53 | 1.53 | 是 | 字面命中 |
| 163 | F022 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-06] | 1.67 | 1.67 | 是 | 字面命中 |
| 164 | F023 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-07] | 1.97 | 1.97 | 是 | 字面命中 |
| 165 | F024 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-08] | 1.98 | 1.98 | 是 | 字面命中 |
| 166 | F025 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-09] | 2.16 | 2.16 | 是 | 字面命中 |
| 167 | F026 | ⑥ | 转折1 叙述路径 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-10] | 2.44 | 2.44 | 是 | 字面命中 |
| 168 | F027 | ⑥ | 转折1 叙述 BOJ 台阶 | JP_POLICY_RATE[2026-01] | 0.728 | 0.728 | 是 | 字面命中 |
| 169 | F028 | ⑥ | 转折2 叙述路径 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-06] | 2.8 | 2.8 | 是 | 字面命中 |
| 170 | F029 | ⑥ | 转折2 叙述路径 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-07] | 2.9 | 2.9 | 是 | 字面命中 |
| 171 | F030 | ⑥ | 转折2 叙述路径 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-08] | 3.2 | 3.2 | 是 | 字面命中 |
| 172 | F031 | ⑥ | 转折2 叙述路径 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-09] | 3.8 | 3.8 | 是 | 字面命中 |
| 173 | F032 | ⑥ | 转折2 叙述路径 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10] | 4.0 | 4.0 | 是 | 字面命中 |
| 174 | F033 | ⑥ | 转折2 日本同窗 | JP_CPI_YOY 2026-02→2026-05 | [1.27, 1.53] | [1.27, 1.53] | 是 | 字面命中 |
| 175 | F034 | ⑥ | 转折2 先后未定 | 同月分辨率不可判→须写『先后未定』 | true | true | 是 | 字面命中 |
| 176 | F035 | ⑥ | 转折3 过渡月 | JP_POLICY_RATE[2026-06] | 0.841 | 0.841 | 是 | 字面命中 |
| 177 | F036 | ⑥ | 转折3 叙述路径 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-08] | 0.977 | 0.977 | 是 | 字面命中 |
| 178 | F037 | ⑥ | 转折3 叙述路径 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-09] | 1.043 | 1.043 | 是 | 字面命中 |
| 179 | F038 | ⑥ | 转折3 叙述路径 | research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10] | 1.227 | 1.227 | 是 | 字面命中 |
| 180 | F039 | ⑥ | 转折3 先后未定 | 月频台阶 vs 欧央行变更日→须写『先后未定』 | true | true | 是 | 字面命中 |
| 181 | F040 | ⑥ | 三转折=不同事件 | 转折 (metric_id,date) 去重数 / 指标维度数 / 地区数 | [3, 2, 2] | [3, 2, 2] | 是 | 三个不同事件(JP_CPI_YOY@2026-02 / EA_HICP_YOY@2026-05 / JP_POLICY_RATE@2026-07); 指标维度=通胀(日/欧元区两序… |
| 182 | G001 | ⑦ | M1-1 欧元区 2026-02 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-02] | 1.9 | 1.9 | 是 | 字面命中 |
| 183 | G002 | ⑦ | M1-1 欧元区 2026-05 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-05] | 3.2 | 3.2 | 是 | 字面命中 |
| 184 | G003 | ⑦ | M1-1 欧元区 2026-06 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-06] | 2.8 | 2.8 | 是 | 字面命中 |
| 185 | G004 | ⑦ | M1-1 欧元区 2026-10 | research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10] | 4.0 | 4.0 | 是 | 字面命中 |
| 186 | G005 | ⑦ | M1-1 日本 2025-01 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2025-01] | 4.03 | 4.03 | 是 | 字面命中 |
| 187 | G006 | ⑦ | M1-1『高点』用词 | JP_CPI_YOY 2025-01 是否局部峰值 / 是否为其前 12 个月最高 | [true, 4.03] | [true, 4.03] | 是 | 全序列最高为 4.31@2023-01-01(更早年),『2025-01 高点』=局部高点/近一年高点,读法成立 |
| 188 | G007 | ⑦ | M1-1 日本 2025-07 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2025-07] | 3.1 | 3.1 | 是 | 字面命中 |
| 189 | G008 | ⑦ | M1-1 日本 2025-09 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2025-09] | 2.91 | 2.91 | 是 | 字面命中 |
| 190 | G009 | ⑦ | M1-1 日本 2025-10 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2025-10] | 2.99 | 2.99 | 是 | 字面命中 |
| 191 | G010 | ⑦ | M1-1 日本 2026-02 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-02] | 1.27 | 1.27 | 是 | 字面命中 |
| 192 | G011 | ⑦ | M1-1 日本 2026-10 | research_snapshot_20261123.json:series_store.JP_CPI_YOY[2026-10] | 2.44 | 2.44 | 是 | 字面命中 |
| 193 | G012 | ⑦ | M1-1『两度小幅回升』 | JP_CPI_YOY 2025-01..2026-02 月环比上升次数 | 2 | 2 | 是 | 字面命中 |
| 194 | G013 | ⑦ | M1-1『总体回升』用词 | JP_CPI_YOY 2026-02..2026-10 月环比下降次数 / 末值>首值 | [1, true] | [">=1(非逐月)", true] | 是 | 字面命中;2026-04 一处回落(1.46→1.38),故用『总体』而非逐月 |
| 195 | G014 | ⑦ | M1-2 欧央行两次变更幅度 | ECB_MRO 窗内两次变更 (bp) | [25, 25] | [25, 25] | 是 | 字面命中 |
| 196 | G015 | ⑦ | M1-2 2026-06-17 变更前后 | research_snapshot_20261123.json:series_store.ECB_MRO/ECB_DFR 变更点 2026-06-17 (from,to) | [[2.15, 2.4], [2.0, 2.25]] | [[2.15, 2.4], [2.0, 2.25]] | 是 | 字面命中 |
| 197 | G016 | ⑦ | M1-2 2026-09-16 变更前后 | research_snapshot_20261123.json:series_store.ECB_MRO/ECB_DFR 变更点 2026-09-16 (from,to) | [[2.4, 2.65], [2.25, 2.5]] | [[2.4, 2.65], [2.25, 2.5]] | 是 | 字面命中 |
| 198 | G017 | ⑦ | M1-2 推断标注 | 冻结日历 ECB 实录条数 / 决议日须标【推断】 | [0, true] | [0, true] | 是 | 字面命中 |
| 199 | G018 | ⑦ | M1-2 其余台阶无实录 | JP_POLICY_RATE 窗内 6 个变动点中,前 45 天内有日历 JP_POLICY_TARGET 决议实录者 | ["2026-10-01"] | ["2026-10-01"] | 是 | 字面命中 |
| 200 | G019 | ⑦ | 机制链证据分级 | l3.mechanism_chains[0].links[*].evidence_level | ["E1", "E1", "E2", "E2"] | ["E1", "E1", "E2", "E2"] | 是 |  |
| 201 | G020 | ⑦ | E2 环假设标注 | links[2].text 以『传导【假设】』起始 / links[3].text 归因含【假设·归因】 | [true, true] | [true, true] | 是 |  |
| 202 | G021 | ⑦ | E1 环事实位措辞 | links[0..1].text 不含『【假设】』 | [false, false] | [false, false] | 是 | E1 环只含【事实】与【推断】标注,推断(决议日回推)逐处标明 |
| 203 | G022 | ⑦ | M1-3 EURUSD 窗起 | research_snapshot_20261123.json:series_store.EURUSD[2026-10-23] | 1.122146 | 1.1221 | 是 | 字面命中 |
| 204 | G023 | ⑦ | M1-3 EURUSD 11-20 收盘 | research_snapshot_20261123.json:series_store.EURUSD[2026-11-20] | 1.096972 | 1.097 | 是 | 字面命中 |
| 205 | G024 | ⑦ | M1-3 EURUSD 月窗变动 | EURUSD 2026-10-23→2026-11-20 | -2.24 | -2.24 | 是 | 字面命中 |
| 206 | G025 | ⑦ | M1-3 USDJPY 窗起 | research_snapshot_20261123.json:series_store.USDJPY[2026-10-23] | 156.494003 | 156.494 | 是 | 字面命中 |
| 207 | G026 | ⑦ | M1-3 USDJPY 11-20 收盘 | research_snapshot_20261123.json:series_store.USDJPY[2026-11-20] | 159.707001 | 159.707 | 是 | 字面命中 |
| 208 | G027 | ⑦ | M1-3 USDJPY 月窗变动 | USDJPY 2026-10-23→2026-11-20 | 2.05 | 2.05 | 是 | 字面命中 |
| 209 | G028 | ⑦ | M1-3 DXY 窗起 | research_snapshot_20261123.json:series_store.DXY[2026-10-23] | 101.809998 | 101.81 | 是 | 字面命中 |
| 210 | G029 | ⑦ | M1-3 DXY 11-20 收盘 | research_snapshot_20261123.json:series_store.DXY[2026-11-20] | 103.809998 | 103.81 | 是 | 字面命中 |
| 211 | G030 | ⑦ | M1-3 DXY 月窗变动 | DXY 2026-10-23→2026-11-20 | 1.96 | 1.96 | 是 | 字面命中 |
| 212 | G031 | ⑦ | M1-3 EURUSD 11-23 盘中 | research_snapshot_20261123.json:series_store.EURUSD[2026-11-23] | 1.093972 | 1.094 | 是 | 字面命中 |
| 213 | G032 | ⑦ | M1-3 EURUSD 至截止变动 | EURUSD 2026-10-23→2026-11-23 | -2.51 | -2.51 | 是 | 字面命中 |
| 214 | G033 | ⑦ | M1-3 USDJPY 11-23 盘中 | research_snapshot_20261123.json:series_store.USDJPY[2026-11-23] | 159.347 | 159.347 | 是 | 字面命中 |
| 215 | G034 | ⑦ | M1-3 USDJPY 至截止变动 | USDJPY 2026-10-23→2026-11-23 | 1.82 | 1.82 | 是 | 字面命中 |
| 216 | G035 | ⑦ | M1-3 DXY 11-23 盘中 | research_snapshot_20261123.json:series_store.DXY[2026-11-23] | 104.079002 | 104.079 | 是 | 字面命中 |
| 217 | G036 | ⑦ | M1-3 DXY 至截止变动 | DXY 2026-10-23→2026-11-23 | 2.23 | 2.23 | 是 | 字面命中 |
| 218 | G037 | ⑦ | M1-3 EURJPY 合成 10-23 | EURUSD×USDJPY @2026-10-23 (1.1221×156.4940=175.60912) | 175.61 | 175.61 | 是 | 字面命中 |
| 219 | G038 | ⑦ | M1-3 EURJPY 合成 11-20 | EURUSD×USDJPY @2026-11-20 (175.1941) | 175.19 | 175.19 | 是 | 字面命中 |
| 220 | G039 | ⑦ | M1-3 EURJPY 合成月窗变动 | 合成交叉盘 2026-10-23→2026-11-20 (全精度) | -0.24 | -0.24 | 是 | 字面命中 |
| 221 | G040 | ⑦ | M1-3 EURJPY 合成 11-23 | EURUSD×USDJPY @2026-11-23 (174.32116) | 174.32 | 174.32 | 是 | 字面命中 |
| 222 | G041 | ⑦ | M1-3 EURJPY 至截止变动 | 合成交叉盘 2026-10-23→2026-11-23 (全精度 -0.7334%) | -0.73 | -0.73 | 是 | 字面命中 |
| 223 | G042 | ⑦ | M1-3 EURJPY 至截止变动(展示值路径) | 174.32/175.61−1 | -0.73 | -0.73 | 是 | 两条舍入路径(全精度/展示值)结果相同 |
| 224 | G043 | ⑦ | M1-3 交叉盘缺席 | series_store 含 EURJPY 键 | [] | [] | 是 | 字面命中 |
| 225 | G044 | ⑦ | M1-4 同日收盘口径窗端点 | SPX/NIKKEI225/DAX/CAC40/VIX 在 2026-10-23 与 2026-11-20 均有观测 | true | true | 是 | 字面命中 |
| 226 | G045 | ⑦ | M1-4 SPX | SPX 2026-10-23→2026-11-20 (7623.68→6910.39) | -9.36 | -9.36 | 是 | 字面命中 |
| 227 | G046 | ⑦ | M1-4 NIKKEI225 | NIKKEI225 2026-10-23→2026-11-20 (62693.16→56436.65) | -9.98 | -9.98 | 是 | 字面命中 |
| 228 | G047 | ⑦ | M1-4 DAX | DAX 2026-10-23→2026-11-20 (25181.65→24802.78) | -1.5 | -1.5 | 是 | 字面命中 |
| 229 | G048 | ⑦ | M1-4 CAC40 | CAC40 2026-10-23→2026-11-20 (7782.82→7927.75) | 1.86 | 1.86 | 是 | 字面命中 |
| 230 | G049 | ⑦ | M1-4 VIX 窗起 | research_snapshot_20261123.json:series_store.VIX[2026-10-23] | 19.450001 | 19.45 | 是 | 字面命中 |
| 231 | G050 | ⑦ | M1-4 VIX 11-20 收盘 | research_snapshot_20261123.json:series_store.VIX[2026-11-20] | 35.889999 | 35.89 | 是 | 字面命中 |
| 232 | G051 | ⑦ | M1-4 VIX 月窗幅度 | VIX 2026-10-23→2026-11-20 | 84.5 | 84.5 | 是 | 字面命中 |
| 233 | G052 | ⑦ | M1-4 VIX 末六日路径 | research_snapshot_20261123.json:series_store.VIX[2026-11-13] | 19.299999 | 19.3 | 是 | 字面命中 |
| 234 | G053 | ⑦ | M1-4 VIX 末六日路径 | research_snapshot_20261123.json:series_store.VIX[2026-11-16] | 22.91 | 22.91 | 是 | 字面命中 |
| 235 | G054 | ⑦ | M1-4 VIX 末六日路径 | research_snapshot_20261123.json:series_store.VIX[2026-11-17] | 25.459999 | 25.46 | 是 | 字面命中 |
| 236 | G055 | ⑦ | M1-4 VIX 末六日路径 | research_snapshot_20261123.json:series_store.VIX[2026-11-18] | 24.559999 | 24.56 | 是 | 字面命中 |
| 237 | G056 | ⑦ | M1-4 VIX 末六日路径 | research_snapshot_20261123.json:series_store.VIX[2026-11-19] | 28.440001 | 28.44 | 是 | 字面命中 |
| 238 | G057 | ⑦ | M1-4 VIX 末六日路径 | research_snapshot_20261123.json:series_store.VIX[2026-11-20] | 35.889999 | 35.89 | 是 | 字面命中 |
| 239 | G058 | ⑦ | M1-4『末六个交易日』 | VIX 序列 ≤2026-11-20 的最后六个观测日 | ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19",… | ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19",… | 是 | 字面命中 |
| 240 | G059 | ⑦ | M1-4『末五个交易日』 | VIX 序列 2026-11-13 之后 ≤2026-11-20 的观测日数 | 5 | 5 | 是 | 字面命中 |
| 241 | G060 | ⑦ | M1-4 引擎回贴 SPX | research_snapshot_20261123.json:series_store.SPX[2026-11-23] | 7203.850098 | 7203.85 | 是 | 字面命中 |
| 242 | G061 | ⑦ | M1-4 引擎回贴 DAX | research_snapshot_20261123.json:series_store.DAX[2026-11-23] | 25209.449219 | 25209.45 | 是 | 字面命中 |
| 243 | G062 | ⑦ | M1-4 引擎回贴 NIKKEI225 | research_snapshot_20261123.json:series_store.NIKKEI225[2026-11-20] | 56436.65 | 56436.65 | 是 | 字面命中 |
| 244 | G063 | ⑦ | M1-4 引擎回贴 VIX | research_snapshot_20261123.json:series_store.VIX[2026-11-23] | 27.01 | 27.01 | 是 | 字面命中 |
| 245 | G064 | ⑦ | M1-4 先例 VIX 11-04 | research_snapshot_20261123.json:series_store.VIX[2026-11-04] | 16.610001 | 16.61 | 是 | 字面命中 |
| 246 | G065 | ⑦ | M1-4 先例 VIX 11-05 | research_snapshot_20261123.json:series_store.VIX[2026-11-05] | 28.18 | 28.18 | 是 | 字面命中 |
| 247 | G066 | ⑦ | M1-4 先例 VIX 单日 | VIX 2026-11-04→2026-11-05 | 69.66 | 69.66 | 是 | 字面命中 |
| 248 | G067 | ⑦ | M1-4 先例 VIX 11-11 | research_snapshot_20261123.json:series_store.VIX[2026-11-11] | 17.49 | 17.49 | 是 | 字面命中 |
| 249 | G068 | ⑦ | M1-4 先例『四个交易日』 | VIX 2026-11-05 之后至 2026-11-11 的观测日 | 4 | 4 | 是 | 字面命中 |
| 250 | G069 | ⑦ | M1-4 先例 VIX 回落 | VIX 2026-11-05→2026-11-11 | -37.93 | -37.93 | 是 | 字面命中 |
| 251 | G070 | ⑦ | M1-4 先例 SPX 11-05 | SPX 2026-11-04→2026-11-05 (-4.3557%) | -4.36 | -4.36 | 是 | 字面命中 |
| 252 | G071 | ⑦ | M1-4 先例 NIKKEI 11-06 | NIKKEI225 2026-11-05→2026-11-06 | -5.96 | -5.96 | 是 | 字面命中 |
| 253 | G072 | ⑦ | M1-4『下一交易日』 | NIKKEI225 2026-11-05 之后的下一观测日 | 2026-11-06 | 2026-11-06 | 是 | 字面命中 |
| 254 | G073 | ⑦ | M1-4 发布日 VIX 11-16 | VIX 2026-11-13→2026-11-16 (18.7047%) | 18.7 | 18.7 | 是 | 字面命中 |
| 255 | G074 | ⑦ | M1-4 发布日 VIX 11-20 | VIX 2026-11-19→2026-11-20 (26.1955%) | 26.2 | 26.2 | 是 | 字面命中 |
| 256 | G075 | ⑦ | M1-4『窗内两个最大单日跳升日』 | 跳升窗(2026-11-16..2026-11-20)单日涨幅前二 | ["2026-11-16", "2026-11-20"] | ["2026-11-16", "2026-11-20"] | 是 | 字面命中;窗=跳升窗; 若取近一月窗则 2026-11-05(+69.66%)最大,原文『跳升窗内』限定成立 |
| 257 | G076 | ⑦ | M1-4/对质环3 跳升窗股指 | SPX 2026-11-13→2026-11-20 (-8.6129%) | -8.61 | -8.61 | 是 | 字面命中 |
| 258 | G077 | ⑦ | M1-4/对质环3 跳升窗股指 | NIKKEI225 2026-11-13→2026-11-20 (-7.6963%) | -7.7 | -7.7 | 是 | 字面命中 |
| 259 | G078 | ⑦ | M1-4/对质环3 跳升窗股指 | DAX 2026-11-13→2026-11-20 (-7.2792%) | -7.28 | -7.28 | 是 | 字面命中 |
| 260 | G079 | ⑦ | M1-4/对质环3 跳升窗股指 | CAC40 2026-11-13→2026-11-20 (-5.2714%) | -5.27 | -5.27 | 是 | 字面命中 |
| 261 | G080 | ⑦ | M1-4『四地股指跌幅均不深于美股』 | 跳升窗跌幅比较 | true | true | 是 | 字面命中 |
| 262 | G081 | ⑦ | M1-4 发布日汇市单日变动上限 | EURUSD/USDJPY 2026-11-16 与 2026-11-20 单日变动绝对值最大 (0.2293%) | true | true | 是 | 字面命中;逐项: EURUSD@2026-11-16 0.2293%, EURUSD@2026-11-20 0.0209%, USDJPY@2026-11-16 0.0594%, USDJP… |
| 263 | G082 | ⑦ | M1-4 FOMC 纪要 | research_plan.policy_doc_facts FOMC-MINUTES-2026-10.published_on | ["2026-11-18"] | ["2026-11-18"] | 是 | 字面命中 |
| 264 | G083 | ⑦ | 对质环3 距最近政策日 | 2026-11-13 − 2026-10-30 (天) | 14 | 14 | 是 | 字面命中 |
| 265 | G084 | ⑦ | 对质环3 距 ECB 最近生效日(起点) | 2026-11-13 − 2026-09-16 (天) | 58 | 58 | 是 | 字面命中 |
| 266 | G085 | ⑦ | 对质环3 距最近政策日(终点) | 2026-11-20 − 2026-10-30 (天) | 21 | 21 | 是 | 字面命中 |
| 267 | G086 | ⑦ | 对质环3 距 ECB 最近生效日(终点) | 2026-11-20 − 2026-09-16 (天) | 65 | 65 | 是 | 字面命中 |
| 268 | G087 | ⑦ | 对质环3 纪要发布后 VIX | VIX 2026-11-18/11-19/11-20 收盘 | [24.56, 28.44, 35.89] | [24.56, 28.44, 35.89] | 是 | 字面命中 |
| 269 | G088 | ⑦ | 对质环1 决议日前可见(2026-06-11) | EA_HICP_YOY 推定规则(月末+16天): 发布日≤2026-06-11 的最新观测月 | ["2026-04", 3.0] | ["2026-04", 3.0] | 是 | 字面命中 |
| 270 | G089 | ⑦ | 对质环1 生效日前可见(2026-06-17) | 同上 发布日≤2026-06-17 | ["2026-05", 3.2] | ["2026-05", 3.2] | 是 | 字面命中 |
| 271 | G090 | ⑦ | 对质环1 决议日前可见(2026-09-10) | 同上 发布日≤2026-09-10 | ["2026-07", 2.9] | ["2026-07", 2.9] | 是 | 字面命中 |
| 272 | G091 | ⑦ | 对质环1 生效日前可见(2026-09-16) | 同上 发布日≤2026-09-16 | ["2026-08", 3.2] | ["2026-08", 3.2] | 是 | 字面命中 |
| 273 | G092 | ⑦ | 对质环1 发布日=生效日同日 | EA_HICP_YOY 2026-08 观测月推定发布日 | 2026-09-16 | 2026-09-16 | 是 | 字面命中 |
| 274 | G093 | ⑦ | 对质环1 日历两档形态(第一次) | 快报=次月首日: ≤2026-06-11 可见最新观测月 | ["2026-05", 3.2] | ["2026-05", 3.2] | 是 | 字面命中 |
| 275 | G094 | ⑦ | 对质环1 日历两档形态(第二次) | 快报=次月首日: ≤2026-09-10 可见最新观测月 | ["2026-08", 3.2] | ["2026-08", 3.2] | 是 | 字面命中 |
| 276 | G095 | ⑦ | 对质环1『变更前读数均高于 2026-02 的 1.9』 | 四个变更前可见读数 vs EA_HICP_YOY[2026-02]=1.9 | true | true | 是 | 字面命中 |
| 277 | G096 | ⑦ | 对质环1 维持天数 | 2025-06-11 → 2026-06-17 (天) | 371 | 371 | 是 | 字面命中 |
| 278 | G097 | ⑦ | 对质环1 维持期无变更 | ECB_MRO/ECB_DFR 在 (2025-06-11, 2026-06-17) 内变更点 | [] | [] | 是 | 字面命中 |
| 279 | G098 | ⑦ | 对质环1 维持期读数 | EA_HICP_YOY 2026-01 / 2026-04 | [1.7, 3.0] | [1.7, 3.0] | 是 | 字面命中 |
| 280 | G099 | ⑦ | 对质环1『2.9 低于 2026-05 峰值 3.2』 | 决议日前可见读数 2.9 vs 2026-05=3.2 且 2026-05 为局部峰值(3.0/3.2/2.8) | [true, true] | [true, true] | 是 | 字面命中 |
| 281 | G100 | ⑦ | 对质环1 样本数 | ECB_MRO 近十二月窗内变更次数 | 2 | 2 | 是 | 字面命中 |
| 282 | G101 | ⑦ | 对质环2 窗内无政策变动点 | ECB/Fed 序列变更点、JP_POLICY_RATE 变动点、日央行决议实录 落在 [2026-10-23, 2026-11-23] | [] | [] | 是 | 字面命中;日央行 2026-10-30 为维持决议(kind=policy_maintenance),不构成变动点 |
| 283 | G102 | ⑦ | 对质环1 区分指标在场 | 区分指标 EA_HICP_YOY 在 series_store / 证据索引 | [true, ["EA_HICP_YOY@2026-10-01"]] | [true, ["EA_HICP_YOY@2026-10-01"]] | 是 | 区分指标须在场且两解释预期方向不同(见 PROSE 六查) |
| 284 | G103 | ⑦ | 对质环2 区分指标在场 | 区分指标 EURUSD 在 series_store / 证据索引 | [true, ["EURUSD@2026-11-23"]] | [true, ["EURUSD@2026-11-23"]] | 是 | 区分指标须在场且两解释预期方向不同(见 PROSE 六查) |
| 285 | G104 | ⑦ | 对质环3 区分指标在场 | 区分指标 VIX 在 series_store / 证据索引 | [true, ["VIX@2026-11-23"]] | [true, ["VIX@2026-11-23"]] | 是 | 区分指标须在场且两解释预期方向不同(见 PROSE 六查) |
| 286 | H001 | ⑧ | 类比 扫描数 | report.json:steps[S6_analog].envelope.data.candidates.scanned | 1871 | 1871 | 是 | 字面命中 |
| 287 | H002 | ⑧ | 类比 有效数 | candidates.valid | 74 | 74 | 是 | 字面命中 |
| 288 | H003 | ⑧ | 类比 TOP1 候选月 | envelope.data.top[0].candidate_month | 2025-03 | 2025-03 | 是 | 字面命中 |
| 289 | H004 | ⑧ | 类比 TOP1 距离 | envelope.data.top[0].distance | 0.727 | 0.727 | 是 | 字面命中 |
| 290 | H005 | ⑧ | 历史类比段数 | reader_map.history_periods | 0 | 0 | 是 | 字面命中 |
| 291 | H006 | ⑧ | 类比能力已执行 | steps[S6_analog].ok / executed | [true, true] | [true, true] | 是 | 字面命中 |
| 292 | H007 | ⑧ | 零段类比=不引事后结果 | agent_judgment.json 中出现候选月『2025-03』的字段路径 | [".reader_map.history_zero_case_note"] | [".reader_map.history_zero_case_note"] | 是 | 字面命中;候选月仅出现于零段注记,无任何『随后 N 个月结果』数字 |
| 293 | I001 | ⑨ | S1 时限晚于入档 | 2026-12 观测月按推定规则发布日 EA=2027-01-16 / JP=2027-01-20 vs deadline | [true, true] | [true, true] | 是 | 字面命中 |
| 294 | I002 | ⑨ | S2 时限 | 同上 vs S2 deadline | 2027-02-15 | 2027-02-15 | 是 | 字面命中 |
| 295 | I003 | ⑨ | S1 证伪指标可观测 | falsification.metric_id 在注册表与证据索引 | [true, true, true] | [true, true, true] | 是 |  |
| 296 | I005 | ⑨ | S1 次证伪指标可观测 | falsification.secondary_metric_ids 在注册表 | [true] | [true] | 是 |  |
| 297 | I004 | ⑨ | S2 证伪指标可观测 | falsification.metric_id 在注册表与证据索引 | [true, true, true] | [true, true, true] | 是 |  |
| 298 | I006 | ⑨ | S2 次证伪指标可观测 | falsification.secondary_metric_ids 在注册表 | [true] | [true] | 是 |  |
| 299 | I007 | ⑨ | 触发用 VIX 可观测 | VIX 在 series_store / 证据索引 | [true, true] | [true, true] | 是 | 字面命中 |
| 300 | I008 | ⑨ | 情景尚未被截止日数据判定 | 两序列在快照内的最后观测月(2026-11/2026-12 读数截止日尚未发布) | ["2026-10", "2026-10"] | ["2026-10", "2026-10"] | 是 | 字面命中 |
| 301 | I009 | ⑨ | 阈值与截止日读数相容 | 截止日读数 EA=4.0(触发≥4.0/证伪<3.5) JP=2.44(≥2.0/<2.0) VIX 11-20 收盘=35.889999(>30/<25) | [true, true, true] | [true, true, true] | 是 | 截止日读数落在两情景之间(未决),两情景方向互补 |
| 302 | I010 | ⑨ | 两情景方向互补 | S1『维持 3.5% 以上/维持 2.0% 以上』 vs S2『回落至 3.0% 以下/回落至 2.0% 以下』 | [true, true, true] | [true, true, true] | 是 |  |
| 303 | I011 | ⑨ | S2 中间区间如实 | S2 证伪阈值 3.5 与触发阈值 3.0 之间既不触发也不证伪 | true | true | 是 | 字面命中 |
| 304 | I012 | ⑨ | 政策分量不可数值核验的披露 | 冻结日历 ECB 实录条数 vs 情景披露 | 0 | 0 | 是 | 字面命中 |
| 305 | I013 | ⑨ | S1 证据引用可解析 | asset_direction.evidence_refs ⊂ 证据索引 | [] | [] | 是 | refs=NIKKEI225@2026-11-20,VIX@2026-11-23 |
| 306 | I014 | ⑨ | S2 证据引用可解析 | asset_direction.evidence_refs ⊂ 证据索引 | [] | [] | 是 | refs=VIX@2026-11-23,NIKKEI225@2026-11-20 |
| 307 | I015 | ⑨ | S1 日本目标现值 | 日历 RC-JP-BOJ-TARGET-2026-09.target_value vs 情景『目标现约 1.25%』 | [1.25] | [1.25] | 是 | 字面命中 |
| 308 | I016 | ⑨ | S2 日本目标现值 | 同上 vs S2『BOJ 维持目标约 1.25% 不变』 | [1.25] | [1.25] | 是 | 字面命中 |
| 309 | I017 | ⑨ | S2 资产方向所引近一月观察 | SPX/NIKKEI225/DAX/CAC40 2026-10-23→2026-11-20 | [-9.36, -9.98, -1.5, 1.86] | [-9.36, -9.98, -1.5, 1.86] | 是 | 字面命中 |
| 310 | J001 | ⑩ | 总判断方向相反 | 日本同比下降 / 欧元区同比上升 | [true, true] | [true, true] | 是 | 字面命中 |
| 311 | J002 | ⑩ | 对质裁定取值 | transmission.links[*].face_off_verdict | ["尚不能区分"] | ["尚不能区分"] | 是 |  |
| 312 | J003 | ⑩ | 对质裁定计数 | 『尚不能区分』环数 | 3 | 3 | 是 | 字面命中 |
| 313 | J004 | ⑩ | L3 引用条数 | contradictions[*].evidence_refs + mechanism_chains[*].links[*].evidence_refs | 20 | 20 | 是 | 字面命中 |
| 314 | J005 | ⑩ | L3 引用全部解析 | L3 引用不在证据索引者 | [] | [] | 是 | 字面命中 |
| 315 | J006 | ⑩ | L3 引用类型 | L3 引用在证据索引中的 kind 集合 | ["snapshot_fact"] | ["snapshot_fact"] | 是 |  |
| 316 | J007 | ⑩ | L4 引用全部解析 | L4 evidence_refs 不在证据索引者 | [] | [] | 是 | L4 引用 4 条 |
| 317 | J008 | ⑩ | 证据索引行数 | report.json:evidence_index 行数 | 60 | 60 | 是 | 字面命中 |
| 318 | J009 | ⑩ | 证据索引构成 | kind 计数 | {"s3_envelope": 25, "snapshot_fact": 35} | {"snapshot_fact": 35, "s3_envelope": 25} | 是 |  |
| 319 | J010 | ⑩ | 点值格数 | research_plan.point_values.cells | 6 | 6 | 是 | 字面命中 |
| 320 | J011 | ⑩ | 日历版本 | release_calendar.json version / updated | ["v1.5.0", "2026-11-21"] | ["v1.5.0", "2026-11-21"] | 是 | 字面命中 |
| 321 | J012 | ⑩ | 总判断与 C2 政策水平一致 | ECB_MRO/ECB_DFR 现行水平与日历 BOJ 目标; 总判断(阿拉伯数字)与 C2(中文数字)两处字面 | [2.65, 2.5, 1.25] | [2.65, 2.5, 1.25] | 是 | 字面命中;C2 字面: 『二点六五』『2.5%』『一点二五』; 总判断字面: 『2.65%』『2.5%』『1.25%』 |
| 322 | J013 | ⑩ | 读者报告 欧央行生效日滞后 | cutoff − 2026-09-16 = 68 天; MAP_REPORT 政策表 | true | true | 是 | 字面命中 |
| 323 | J014 | ⑩ | 渲染一致性: 总判断+三条矛盾陈述 | agent_judgment.json 总判断+三条矛盾陈述 共 4 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 1, "in_FULL": 3, "in_report": 3, "not_rendered_anywhere": [… | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 1/4、FULL 3/4、report 3/4;三件均缺席 0 段 |
| 324 | J015 | ⑩ | 渲染一致性: 机制链四环 | agent_judgment.json 机制链四环 共 4 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 0, "in_FULL": 4, "in_report": 4, "not_rendered_anywhere": [… | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 0/4、FULL 4/4、report 4/4;三件均缺席 0 段 |
| 325 | J016 | ⑩ | 渲染一致性: 两地走位 | agent_judgment.json 两地走位 共 2 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 2, "in_FULL": 0, "in_report": 0, "not_rendered_anywhere": [… | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 2/2、FULL 0/2、report 0/2;三件均缺席 0 段 |
| 326 | J017 | ⑩ | 渲染一致性: 传导对质三环(结构字段) | agent_judgment.json 传导对质三环(结构字段) 共 18 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 18, "in_FULL": 4, "in_report": 4, "not_rendered_anywhere": … | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 18/18、FULL 4/18、report 4/18;三件均缺席 0 段 |
| 327 | J018 | ⑩ | 渲染一致性: 三转折(谁先变/跟进背离) | agent_judgment.json 三转折(谁先变/跟进背离) 共 6 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 6, "in_FULL": 0, "in_report": 0, "not_rendered_anywhere": [… | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 6/6、FULL 0/6、report 0/6;三件均缺席 0 段 |
| 328 | J019 | ⑩ | 渲染一致性: 两情景 | agent_judgment.json 两情景 共 8 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 6, "in_FULL": 8, "in_report": 8, "not_rendered_anywhere": [… | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 6/8、FULL 8/8、report 8/8;三件均缺席 0 段 |
| 329 | J021 | ⑩ | 渲染一致性: 历史类比零段注记 | agent_judgment.json 历史类比零段注记 共 1 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 1, "in_FULL": 0, "in_report": 0, "not_rendered_anywhere": [… | {"not_rendered_anywhere": []} | 是 | 逐字在场(去空白): MAP 1/1、FULL 0/1、report 0/1;三件均缺席 0 段 |
| 330 | J022 | ⑩ | 读者报告总判断逐字 | MAP_REPORT.md 含总判断原文(去空白) | true | true | 是 |  |
| 331 | J023 | ⑩ | C2 截止日盘中水平 | USDJPY/SPX/VIX @2026-11-23 | [159.35, 7203.85, 27.01] | [159.35, 7203.85, 27.01] | 是 | 字面命中 |
| 332 | J024 | ⑩ | C2 盘中口径 | 三序列 2026-11-23 为快照日观测(非 11-20 收盘) | true | true | 是 | 字面命中 |
| 333 | K001 | ⑪ | C1 东京CPI Gate A 名单 | snapshot.gate_a.noncore_missing | true | true | 是 | 字面命中 |
| 334 | K002 | ⑪ | C1 东京CPI 缺席注记(逐字) | snapshot.gate_a.noncore_missing_detail.JP_CPI_TOKYO_YOY | 来源文件在场而指标缺席 | 来源文件在场而指标缺席 | 是 | 字面命中;快照全文: 来源文件在场而指标缺席(采集遗漏或子源缺席——档内无该指标子源状态记录,不可区分) |
| 335 | K003 | ⑪ | C1 东京CPI 无 L1 事实行 | report.layers.L1 rows metric_id | false | false | 是 | 字面命中 |
| 336 | K004 | ⑪ | 读者报告 Gate A 行与快照名单一致 | snapshot.gate_a.{status,noncore_missing,noncore_degraded} | DEGRADED | DEGRADED | 是 | 字面命中;名单 7 缺席/8 降级逐字在场于 MAP_REPORT.md 第7行 |
| 337 | K005 | ⑪ | C1 L1 质量位 WARN/WARN | report.layers.L1 rows quality_status | ["WARN", "WARN"] | ["WARN", "WARN"] | 是 | 字面命中 |
| 338 | K006 | ⑪ | C1 WARN 原因=发布时间未验证 | snapshot.facts[*].issues | [true, true] | [true, true] | 是 | 字面命中;JP_CPI_YOY: release:JP_CPI_YOY发布时间未验证(RELEASE_UNKNOWN: 采集端未携带release_date)——点时可得性未认证,新鲜度仅按… |
| 339 | K007 | ⑪ | C3 L1 质量位 DEGRADED | report.layers.L1 rows quality_status | ["DEGRADED", "DEGRADED"] | ["DEGRADED", "DEGRADED"] | 是 | 字面命中 |
| 340 | K008 | ⑪ | C3 Gate A degraded 名单 | snapshot.gate_a.noncore_degraded | ["ECB_DFR", "ECB_MRO"] | ["ECB_DFR", "ECB_MRO"] | 是 | 字面命中 |
| 341 | K009 | ⑪ | C3 滞后天数与快照 DEGRADED 原因一致 | snapshot.facts[*].issues | [true, true] | [true, true] | 是 | 字面命中;ECB_MRO: frequency:ECB_MRO观测日滞后68天(>10天有效窗,daily频;未发布或采集失败,不得当作最新一期) |
| 342 | K010 | ⑪ | 对质环2 交叉盘缺席(序列面+注册表) | snapshot.series_store keys / registry metric_id | [false, false] | [false, false] | 是 | 字面命中 |
| 343 | K011 | ⑪ | C1 竞争解释『无分项构成序列』 | registry metric_id(CORE\|ENERG, economy in EA/JP) | [] | [] | 是 | 字面命中 |
| 344 | K012 | ⑪ | C2 竞争解释『无央行表态文本序列』 | registry metric_id(STATE\|SPEECH\|TEXT\|MINUTE\|SENTIM\|SURVEY) | [] | [] | 是 | 字面命中 |
| 345 | K013 | ⑪ | Q4 JP_POLICY_TARGET 注册表不可得 | report.research_plan.dimension_gaps / registry | [false, ["registry_absent"]] | [false, ["registry_absent"]] | 是 | 字面命中 |
| 346 | K014 | ⑪ | C1 东京序列起点(注册表注记) | registry JP_CPI_TOKYO_YOY.calc | true | true | 是 | 字面命中 |
| 347 | L001 | ⑫ | C2/Q4 截止日盘中水平: 7 序列当日有观测 | snapshot.series_store.<m> 末观测日 | [["SPX", "2026-11-23"], ["VIX", "2026-11-23"], ["DAX", "2026-11-23"], … | [["SPX", "2026-11-23"], ["VIX", "2026-11-23"], ["DAX", "2026-11-23"], … | 是 | 字面命中 |
| 348 | L002 | ⑫ | 盘中佐证: 当日值落在日内低/高之间 | snapshot.facts[*].{low,value,high} | true | true | 是 | 字面命中;SPX low 7181.08/value 7203.85/high 7260.17; VIX low 26.8/value 27.01/high 35.08; DAX low 2… |
| 349 | L003 | ⑫ | M1-4 日经末观测日=2026-11-20 | snapshot.series_store.NIKKEI225 末观测日 | 2026-11-20 | 2026-11-20 | 是 | 字面命中 |
| 350 | L004 | ⑫ | 盘中相容: 纽约开盘后/柏林收盘前/截止日为交易日 | snapshot.research_as_of 时区换算(常规交易时段 09:30-16:00 纽约、09:00-17:30 柏林) | [true, true, true] | [true, true, true] | 是 | 字面命中;快照时刻 2026-11-23T22:53:47+08:00 = 纽约 09:53(Mon) / 柏林 15:53 / 东京 23:53 / 上海 22:53 |
| 351 | L005 | ⑫ | 时序: 快照时刻 < 运行起始 < 成文时刻 | snapshot.research_as_of / report.run.ts_utc / agent_declaration.written_at | [true, true] | [true, true] | 是 | as_of 2026-11-23 14:53:47+00:00 \| run 2026-11-23 21:33:36+00:00 \| written 2026-11-23 21:… |
| 352 | L006 | ⑫ | 截止日当日事实 as_of 与 research_as_of 一致 | snapshot.facts[*].as_of | ["2026-11-23T22:53:47+08:00"] | ["2026-11-23T22:53:47+08:00"] | 是 |  |
| 353 | L007 | ⑫ | M1-3 UST_10Y 末观测日 | snapshot.series_store.UST_10Y 末观测日 | 2026-11-19 | 2026-11-19 | 是 | 字面命中 |
| 354 | L008 | ⑫ | 同日收盘口径两端为交易日且有观测 | snapshot.series_store 8 序列在 2026-10-23/2026-11-20 的观测 | true | true | 是 | 字面命中 |
| 355 | L009 | ⑫ | 截止日与其前一交易日星期 | 日历 | ["Mon", "Fri"] | ["Mon", "Fri"] | 是 | 11-21/11-22 为周末;快照时刻东京 23:53 已晚于当日东京场收盘,日经 11-23 观测缺席属采集滞后,席位未把 11-20 值写成截止日值 |
| 356 | M001 | ⑬ | 契约逐位核验状态 | agent_judgment.contract_verification.verdicts[*] | [["ECB_DFR", "STALE"], ["JP_POLICY_RATE", "VERIFIED"], ["USDJPY", "VER… | [["ECB_DFR", "STALE"], ["JP_POLICY_RATE", "VERIFIED"], ["USDJPY", "VER… | 是 |  |
| 357 | M002 | ⑬ | STALE 位数值=序列直读 | verdicts[STALE] + snapshot.series_store.ECB_DFR[2026-09-16] | ["2.5%", 2.5, 2.5, 2.5] | ["2.5%", 2.5, 2.5, 2.5] | 是 | STALE 为时效状态而非数值不符;contradicted=0 |
| 358 | M003 | ⑬ | STALE 与 L1 DEGRADED 一一对应 | verdicts[*].metric × report.layers.L1 quality_status | [["ECB_DFR"], ["ECB_DFR"]] | [["ECB_DFR"], ["ECB_DFR"]] | 是 | 五个受核指标中仅 ECB_DFR 在 L1 为 DEGRADED;JP_POLICY_RATE 为 WARN 仍 VERIFIED——STALE 源于时效位 |
| 359 | M004 | ⑬ | 契约总判与统计 | agent_judgment.contract_verification.{verdict,stats} | ["VERIFIED", 5, 4, 0, 0] | ["VERIFIED", 5, 4, 0, 0] | 是 |  |
| 360 | M005 | ⑬ | STALE 根因(ECB_DFR DEGRADED)已在判断档披露 | agent_judgment 全文检索 | [false, true, true] | [false, true, true] | 是 | 契约核验发生在成文之后,席位无从写『STALE』字样;其根因与时效风险已由 C3/QN4/总判断披露,数值经本席直读一致 |
| 361 | N001 | ⑭ | 欧央行 2026-09-16 后状态未被写成『无变化/维持』(事实位) | agent_judgment 全文分句扫描(欧央行+维持类词) | 0 | 0 | 是 | 命中 5 句均为情景假设/竞争解释/带『不可见·不可判·尚未验证』限定;事实位零命中 |
| 362 | N002 | ⑭ | C2 无未生效决议限定于引擎记录面 | agent_judgment.l3.contradictions[1].statement | true | true | 是 | 字面命中 |
| 363 | N003 | ⑭ | C2 其后决议面不可见【尚未验证】 | agent_judgment.l3.contradictions[1].statement | true | true | 是 | 字面命中 |
| 364 | N004 | ⑭ | C3 结论覆盖面限定 | agent_judgment.l3.contradictions[2].statement | true | true | 是 | 字面命中 |
| 365 | N005 | ⑭ | 日历零 ECB 条目 / 零待生效条目 | release_calendar.entries | [[], []] | [[], []] | 是 | 日历 18 条,version 1.5.0,updated 2026-11-21 |
| 366 | N006 | ⑭ | C2 日央行确认维持=维持决议且目标值未变 | release_calendar RC-JP-BOJ-MAINT-2026-10 / RC-JP-BOJ-TARGET-2026-09 | ["policy_maintenance", 1.25, false, 1.25] | ["policy_maintenance", 1.25, false, 1.25] | 是 | 字面命中 |
| 367 | N007 | ⑭ | C2 日央行『收紧』方向标注【推断】 | agent_judgment.l3.contradictions[1].statement | [true, true] | [true, true] | 是 | 字面命中 |
| 368 | N008 | ⑭ | 总判断未把月均值写成官方目标 | agent_judgment.reader_map.headline_conclusion | [false, false, false] | [false, false, false] | 是 | 总判断目标值仅 1.25(日历宣布值);月均 1.227 只出现在 C2/走位/机制链并带『月均口径』 |
| 369 | N009 | ⑭ | 月均≠宣布值 两处写明 | agent_judgment C2 / reader_map.regions[1].from_to | [true, true] | [true, true] | 是 | 字面命中 |
| 370 | N010 | ⑭ | 日央行实录无前值字段 | release_calendar RC-JP-BOJ-TARGET-2026-09 字段名 | [] | [] | 是 | 实录字段: basis, decision_date, effective_on, entry_id, first_publish_on_or_after, kind, metri… |
| 371 | N011 | ⑭ | 日历『约1.25%』与总判断『1.25%』 | release_calendar RC-JP-BOJ-TARGET-2026-09.{target_value,note} | [1.25, true, true] | [1.25, true, true] | 是 | 字面命中;数值字段 1.25 精确;日历注记行文为『约1.25%』,总判断与走位未带『约』(见 PROSE NIT) |
| 372 | O001 | ⑮ | C2 日央行三日期分记 | release_calendar RC-JP-BOJ-* | ["2026-09-18", "2026-09-24", "2026-10-30"] | ["2026-09-18", "2026-09-24", "2026-10-30"] | 是 | 字面命中 |
| 373 | O002 | ⑮ | 现行有效目标: 生效日≤截止日≤obs_to,且无待生效 | release_calendar RC-JP-BOJ-TARGET-2026-09 | [true, true, 0] | [true, true, 0] | 是 | 字面命中 |
| 374 | O003 | ⑮ | 欧央行现行生效水平=序列末观测 | snapshot.series_store.ECB_MRO/ECB_DFR 末观测 | [["2026-09-16", 2.65], ["2026-09-16", 2.5]] | [["2026-09-16", 2.65], ["2026-09-16", 2.5]] | 是 | 字面命中 |
| 375 | O004 | ⑮ | Q5④ 两序列含非周三观测 | snapshot.series_store.ECB_MRO/ECB_DFR 观测日星期分布 | [true, true] | [true, true] | 是 | 字面命中;非周三观测数/总观测数: {"ECB_MRO": [9, 48], "ECB_DFR": [21, 69]} |
| 376 | O005 | ⑮ | Q5④ 引擎原句在场 | MAP_REPORT.md 第65行 | true | true | 是 | 字面命中 |
| 377 | O006 | ⑮ | Q5① 契约锚标签硬编码与本档规避 | tree judgment_contract.py (13) 块 / point_values cells anchors / 走位正文 | [true, ["6个月前", "最新一期"], 0] | [true, ["6个月前", "最新一期"], 0] | 是 | 字面命中;本问只有『6个月前/最新一期』两锚,(13) 的标签循环只取到『最新一期』一月,任何 ≥2 个月的『观测 X→Y』串必不成其保序子序列;席位走位正文用『观测月 X』逐锚表述,正则零… |
| 378 | O007 | ⑮ | Q5② 别名表未覆盖五指标 | tree text_consistency.ALIASES keys | [] | [] | 是 | 字面命中;ALIASES 共 72 键;近邻键: ['CN_CPI_YOY', 'CORE_CPI', 'CPI', 'ECB_DFR', 'JP_POLICY_RATE'] |
| 379 | O008 | ⑮ | 陈述层『无别名指标数值用中文数字』自述 | agent_judgment l3.contradictions[*].statement 内指标名近邻的阿拉伯小数值 | ["存款便利利率", "月均"] | ["存款便利利率", "月均"] | 是 | 字面命中;三条矛盾陈述正文里以阿拉伯小数出现的指标值仅『存款便利利率…2.5%』(ECB_DFR)与『月均…1.227%』(JP_POLICY_RATE),二者均有别名并经契约逐位绑定;其余… |
| 380 | O009 | ⑮ | 注册表决策驱动序列口径(两口径并列的依据) | registry ECB_MRO/ECB_DFR.freshness | [true, true, true, 10, 10] | [true, true, true, 10, 10] | 是 | 字面命中;席位只引滞后阈口径(Gate A=degraded);注册表同处另有 decision_dated 口径(无更晚已证实决议不作过期),引擎点值格按后者判 ok——见 PROSE M… |
| 381 | O010 | ⑮ | 引擎点值格对欧央行现值的状态 | report.research_plan.point_values.cells[ECB_*].anchors[最新一期] | ["ok", "policy_confirmation", "2026-09-16", "ok"] | ["ok", "policy_confirmation", "2026-09-16", "ok"] | 是 | 引擎点值格未把欧央行现值标过期/未核验(与 Gate A degraded 并存) |
| 382 | O011 | ⑮ | 同比基期=去年同月(2025-10),非相邻月 | agent_judgment C1 / 总判断 | [true, true, true, true] | [true, true, true, true] | 是 |  |
| 383 | O012 | ⑮ | 读者报告官方记录面(日本行) | MAP_REPORT.md 第71行 + 日历复算 | true | true | 是 | 距上次调整(按生效日)/距决议/距维持 = 60/66/24 天,待生效列『—』 |
| 384 | O014 | ⑮ | 对质环1『决议日前可见读数』的数值(修订口径注记) | snapshot.series_store.EA_HICP_YOY | [3.2, 3.2] | [3.2, 3.2] | 是 | 字面命中;点值格 vintage_semantics=事后回顾(最新修订值,非当时首发值),注册表注明 HICP 近月含回溯修订;判断档未并列此口径(见 PROSE MINOR) |
| 385 | D101 | D-日频点值对 | 判断档日频点值 | series_store.ECB_MRO @2025-06-11 | 2.15 | 2.15 | 是 | 字面命中 |
| 386 | D103 | D-日频点值对 | 判断档日频点值 | series_store.ECB_DFR @2025-06-11 | 2.0 | 2.0 | 是 | 字面命中 |
| 387 | D200 | D-窗长 | JP 走位「近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227」 | JP_POLICY_RATE 月度观测数 2025-11..2026-10 | [12, "2025-11", "2026-10"] | [12, "2025-11", "2026-10"] | 是 | 字面命中 |
| 388 | D201 | D-单日变动 | M1-4/TL3「两日欧元、日元对美元单日变动幅度不超过 0.23%」 | EURUSD/USDJPY 2026-11-16、2026-11-20 单日变动% | [[["EURUSD", "2026-11-16", -0.2293], ["EURUSD", "2026-11-20", -0.0209]… | [4, 0.23] | 是 | 字面命中;[["EURUSD", "2026-11-16", -0.2293], ["EURUSD", "2026-11-20", -0.0209], ["USDJPY", "2026-11… |
| 389 | D202 | D-美联储变动点 | TL2「美联储 2026-09-17 生效」 | DFEDTARU/DFEDTARL 最近变动日 | [["DFEDTARU", "2026-09-17", 4.0, ["2026-11-23", 4.0]], ["DFEDTARL", "2… | ["2026-09-17", "2026-09-17"] | 是 | 字面命中;[["DFEDTARU", "2026-09-17", 4.0, ["2026-11-23", 4.0]], ["DFEDTARL", "2026-09-17", 3.75, ["… |
| 390 | D203 | D-近十二个月最高 | T2 叙事「最新读数为近十二个月最高」 | EA_HICP_YOY 2025-11..2026-10 最大值月 | ["2026-10", 4.0, 12] | ["2026-10", 4.0, 12] | 是 | 字面命中 |
| 391 | D204 | D-口径文字 | M1-1「(新基优先,重叠差>0.10pp 告警)」 | metric_registry.JP_CPI_YOY.calc 含 0.10 告警阈 | [true, true] | [true, true] | 是 | 字面命中;registry calc: 日本全国消费者物价指数(综合同比,含生鲜食品);jp_market_collector fetch_statgo_cpi_yoy 取 stat.go.… |
| 392 | CN001 | E-陈述层中文数字 | C1 日本最新读数 | series_store.JP_CPI_YOY @2026-10 | 2.44 | 2.44 | 是 | 字面命中 |
| 393 | CN002 | E-陈述层中文数字 | C1 欧元区最新读数 | series_store.EA_HICP_YOY @2026-10 | 4.0 | 4.0 | 是 | 字面命中 |
| 394 | CN003 | E-陈述层中文数字 | C1 东京最新读数 | series_store.JP_CPI_TOKYO_YOY @2026-10 | 2.73 | 2.73 | 是 | 字面命中 |
| 395 | CN008 | E-陈述层中文数字 | C2 欧央行 2026-06-17 上调幅度 | ECB_MRO 2026-06-17 变更 | 25.0 | 25 | 是 | 字面命中 |
| 396 | CN009 | E-陈述层中文数字 | C2 欧央行 2026-09-16 上调幅度 | ECB_MRO 2026-09-16 变更 | 25.0 | 25 | 是 | 字面命中 |

### 逐对复核(与上表已覆盖点重复,全中,不重复计数;72 条)

| 编号 | 指标@时点 | 直算值 | 报告值 | 字面 | 已由 |
|---|---|---|---|---|---|
| D001X | series_store.EA_HICP_YOY @2025-11 | 2.1 | 2.1 | 命中 | F015 |
| D002X | series_store.EA_HICP_YOY @2026-01 | 1.7 | 1.7 | 命中 | C015 |
| D003X | series_store.EA_HICP_YOY @2026-02 | 1.9 | 1.9 | 命中 | F006 |
| D004X | series_store.EA_HICP_YOY @2026-04 | 3.0 | 3.0 | 命中 | B001 |
| D005X | series_store.EA_HICP_YOY @2026-05 | 3.2 | 3.2 | 命中 | F007 |
| D006X | series_store.EA_HICP_YOY @2026-06 | 2.8 | 2.8 | 命中 | F028 |
| D007X | series_store.EA_HICP_YOY @2026-07 | 2.9 | 2.9 | 命中 | F029 |
| D008X | series_store.EA_HICP_YOY @2026-08 | 3.2 | 3.2 | 命中 | F030 |
| D009X | series_store.EA_HICP_YOY @2026-09 | 3.8 | 3.8 | 命中 | F031 |
| D010X | series_store.EA_HICP_YOY @2026-10 | 4.0 | 4.0 | 命中 | B004 |
| D011X | series_store.JP_CPI_YOY @2025-01 | 4.03 | 4.03 | 命中 | G005 |
| D012X | series_store.JP_CPI_YOY @2025-07 | 3.1 | 3.1 | 命中 | G007 |
| D013X | series_store.JP_CPI_YOY @2025-09 | 2.91 | 2.91 | 命中 | G008 |
| D014X | series_store.JP_CPI_YOY @2025-10 | 2.99 | 2.99 | 命中 | C001 |
| D015X | series_store.JP_CPI_YOY @2025-11 | 2.9 | 2.9 | 命中 | F002 |
| D016X | series_store.JP_CPI_YOY @2026-02 | 1.27 | 1.27 | 命中 | C016 |
| D017X | series_store.JP_CPI_YOY @2026-03 | 1.46 | 1.46 | 命中 | F019 |
| D018X | series_store.JP_CPI_YOY @2026-04 | 1.38 | 1.38 | 命中 | B019 |
| D019X | series_store.JP_CPI_YOY @2026-05 | 1.53 | 1.53 | 命中 | F021 |
| D020X | series_store.JP_CPI_YOY @2026-06 | 1.67 | 1.67 | 命中 | F022 |
| D021X | series_store.JP_CPI_YOY @2026-07 | 1.97 | 1.97 | 命中 | F023 |
| D022X | series_store.JP_CPI_YOY @2026-08 | 1.98 | 1.98 | 命中 | F024 |
| D023X | series_store.JP_CPI_YOY @2026-09 | 2.16 | 2.16 | 命中 | F025 |
| D024X | series_store.JP_CPI_YOY @2026-10 | 2.44 | 2.44 | 命中 | B022 |
| D025X | series_store.JP_CPI_TOKYO_YOY @2026-04 | 1.42 | 1.42 | 命中 | B025 |
| D026X | series_store.JP_CPI_TOKYO_YOY @2026-10 | 2.73 | 2.73 | 命中 | B028 |
| D027X | series_store.JP_POLICY_RATE @2025-11 | 0.478 | 0.478 | 命中 | D040 |
| D028X | series_store.JP_POLICY_RATE @2026-01 | 0.728 | 0.728 | 命中 | F027 |
| D029X | series_store.JP_POLICY_RATE @2026-04 | 0.727 | 0.727 | 命中 | B031 |
| D030X | series_store.JP_POLICY_RATE @2026-06 | 0.841 | 0.841 | 命中 | F035 |
| D031X | series_store.JP_POLICY_RATE @2026-07 | 0.978 | 0.978 | 命中 | F011 |
| D032X | series_store.JP_POLICY_RATE @2026-08 | 0.977 | 0.977 | 命中 | F036 |
| D033X | series_store.JP_POLICY_RATE @2026-09 | 1.043 | 1.043 | 命中 | D038 |
| D034X | series_store.JP_POLICY_RATE @2026-10 | 1.227 | 1.227 | 命中 | B034 |
| D102X | series_store.ECB_MRO @2026-09-16 | 2.65 | 2.65 | 命中 | D002 |
| D104X | series_store.ECB_DFR @2026-09-16 | 2.5 | 2.5 | 命中 | D003 |
| D105X | series_store.USDJPY @2026-11-23 | 159.347 | 159.35 | 命中 | J023 |
| D106X | series_store.SPX @2026-11-23 | 7203.850098 | 7203.85 | 命中 | G060 |
| D107X | series_store.VIX @2026-11-23 | 27.01 | 27.01 | 命中 | G063 |
| D108X | series_store.UST_10Y @2026-11-19 | 5.04 | 5.04 | 命中 | E016 |
| D109X | series_store.EURUSD @2026-10-23 | 1.122146 | 1.1221 | 命中 | G022 |
| D110X | series_store.EURUSD @2026-11-20 | 1.096972 | 1.097 | 命中 | G023 |
| D111X | series_store.USDJPY @2026-10-23 | 156.494003 | 156.494 | 命中 | G025 |
| D112X | series_store.USDJPY @2026-11-20 | 159.707001 | 159.707 | 命中 | G026 |
| D113X | series_store.DXY @2026-10-23 | 101.809998 | 101.81 | 命中 | G028 |
| D114X | series_store.DXY @2026-11-20 | 103.809998 | 103.81 | 命中 | G029 |
| D115X | series_store.DXY @2026-11-23 | 104.079002 | 104.079 | 命中 | G035 |
| D116X | series_store.EURUSD @2026-11-23 | 1.093972 | 1.094 | 命中 | G031 |
| D117X | series_store.USDJPY @2026-11-23 | 159.347 | 159.347 | 命中 | G033 |
| D118X | series_store.NIKKEI225 @2026-11-20 | 56436.65 | 56436.65 | 命中 | G062 |
| D119X | series_store.DAX @2026-11-23 | 25209.449219 | 25209.45 | 命中 | G061 |
| D120X | series_store.VIX @2026-11-13 | 19.299999 | 19.3 | 命中 | G052 |
| D121X | series_store.VIX @2026-11-16 | 22.91 | 22.91 | 命中 | G053 |
| D122X | series_store.VIX @2026-11-17 | 25.459999 | 25.46 | 命中 | G054 |
| D123X | series_store.VIX @2026-11-18 | 24.559999 | 24.56 | 命中 | G055 |
| D124X | series_store.VIX @2026-11-19 | 28.440001 | 28.44 | 命中 | G056 |
| D125X | series_store.VIX @2026-11-20 | 35.889999 | 35.89 | 命中 | G050 |
| D126X | series_store.VIX @2026-11-04 | 16.610001 | 16.61 | 命中 | G064 |
| D127X | series_store.VIX @2026-11-05 | 28.18 | 28.18 | 命中 | G065 |
| D128X | series_store.VIX @2026-11-11 | 17.49 | 17.49 | 命中 | G067 |
| CN004X | series_store.JP_CPI_YOY @2025-10 | 2.99 | 2.99 | 命中 | C001 的字面覆盖,不… |
| CN005X | series_store.EA_HICP_YOY @2025-10 | 2.1 | 2.1 | 命中 | C004 的字面覆盖,不… |
| CN006X | JP_CPI_YOY 2026-10 − 2025-10 | -0.55 | -0.55 | 命中 | C002 的字面覆盖,不… |
| CN007X | EA_HICP_YOY 2026-10 − 2025-10 | 1.9 | 1.9 | 命中 | C005 的字面覆盖,不… |
| CN010X | series_store.ECB_MRO @2026-09-16 | 2.65 | 2.65 | 命中 | D002,O003 的字… |
| CN011X | series_store.JP_POLICY_RATE @2026-04 | 0.727 | 0.727 | 命中 | D039 的字面覆盖,不… |
| CN012X | series_store.JP_POLICY_RATE @2026-10 | 1.227 | 1.227 | 命中 | D040 的字面覆盖,不… |
| CN013X | series_store.JP_POLICY_RATE @2025-11 | 0.478 | 0.478 | 命中 | D040 的字面覆盖,不… |
| CN014X | 2026-10-30→2026-11-23 | 24 | 24 | 命中 | D025 的字面覆盖,不… |
| CN015X | 2026-09-16→2026-11-23 | 68 | 68 | 命中 | D014,K009 的字… |
| CN016X | metric_registry.ECB_MRO.freshness.max_calendar_lag_days | 10 | 10 | 命中 | D016,O009 的字… |
| CN017X | metric_registry.ECB_DFR.freshness.max_calendar_lag_days | 10 | 10 | 命中 | D016,O009 的字… |

### 范围外观察(引擎渲染/口径面,非判断偏离,不计入命中/偏离;5 条)

| 编号 | 类别 | 位置 | 出处键 | 直算值 | 引擎面值 | 备注 |
|---|---|---|---|---|---|---|
| J017X | ⑩ | 渲染一致性: 传导对质三环(verdict_note 裁定理由) | agent_judgment.json 传导对质三环(verdict_note 裁定理由) 共 3 段原文(去空白)在 MAP/FULL/report 三件中的… | {"in_MAP": 0, "in_FULL": 0, "in_report": 0, "not_rendered_anywhere": ["TL1.verdict_note", "TL2.verdict_note", "TL3.verdi… | 渲染面: 上述字段在三件报告中均缺席 | 逐字在场(去空白): MAP 0/3、FULL 0/3、report 0/3;三件均缺席 3 段 |
| J018X | ⑩ | 渲染一致性: 三转折(narrative 叙述) | agent_judgment.json 三转折(narrative 叙述) 共 3 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 0, "in_FULL": 0, "in_report": 0, "not_rendered_anywhere": ["T1.narrative", "T2.narrative", "T3.narrative"]} | 渲染面: 上述字段在三件报告中均缺席 | 逐字在场(去空白): MAP 0/3、FULL 0/3、report 0/3;三件均缺席 3 段 |
| J020 | ⑩ | 渲染一致性: 质量门注记六条 | agent_judgment.json 质量门注记六条 共 6 段原文(去空白)在 MAP/FULL/report 三件中的出现情况 | {"in_MAP": 0, "in_FULL": 0, "in_report": 0, "not_rendered_anywhere": ["QN0", "QN1", "QN2", "QN3", "QN4", "QN5"]} | 渲染面: 上述字段在三件报告中均缺席 | 逐字在场(去空白): MAP 0/6、FULL 0/6、report 0/6;三件均缺席 6 段 |
| K015 | ⑪ | 东京CPI 点值格状态(引擎面) | report.research_plan.point_values.cells[JP_CPI_TOKYO_YOY].anchors[*].status | ["ok", "ok"] | ["degraded_or_missing", "degraded_or_missing"] | 引擎点值格对 Gate A noncore_missing 序列两锚仍标 ok,读者报告环境表该行亦标 ok(与同页第7行『缺席数据不得进入研究结论』并置);席位在 C1/QN4 按 Gate A 如实披露——引擎面口径不一,非判断偏离 |
| O013 | ⑮ | 引擎面对欧央行决议日的两种表述(范围外) | registry ECB_MRO.{calc,release_semantics} vs 点值格 policy_dates / publication_rule | [true, "2026-09-10", "2026-09-16", "ECB 决议日当日公布(变更日观测)"] | [true, "2026-09-10", "2026-09-16", "ECB 决议日当日公布(变更日观测)"] | 注册表写『决议变更即时生效/当日更新』,读者报告覆盖表把 2026-09-16 写作『决议日当日公布』,政策表却写决议 09-10→生效 09-16——引擎内部口径不一;席位取政策表面并把决议日标【推断】,生效日 09-16 在两种读法下不变 |

### 1.4 本席补充计算(支撑第 2–4 节里本席自己引用的数字;出处=文件+键)

| 编号 | 内容 | 出处键 | 数值 |
|---|---|---|---|
| S01 | 2026-11-16..2026-11-20 逐日收盘变动% | series_store.SPX/NIKKEI225/DAX/CAC40/VIX/EURUSD/USDJPY | SPX -1.92/-1.03/-0.23/-2.02/-3.70; NIKKEI225 -2.42/-1.34/+0.28/+0.71/-5.06; DAX -0.57/-2.08/-1.19/-1.06/-2.60; CAC40 -0.20/-1.62/-0.85/-0.81/-1.89; VIX +18.70/+11.13/-3.53/+15.80/+26.20; EURUSD -0.23/-0.24/-0.05/-0.19/-0.02; USDJPY -0.06/-0.16/-0.01/-0.08/+0.20 |
| S02 | 最新同比读数相对 1/3/6/12 个月前的差;近 12 个月其余各月低于最新值个数 | series_store.JP_CPI_YOY、EA_HICP_YOY | 日本 +0.28/+0.47/+1.06/-0.55(10/11);欧元区 +0.20/+1.10/+1.00/+1.90(11/11) |
| S03 | 月均逐月台阶(bp,进入该月) | series_store.JP_POLICY_RATE | 2025-11 +0.1, 2025-12 +7.9, 2026-01 +17.1, 2026-02 +0.0, 2026-03 +0.0, 2026-04 -0.1, 2026-05 +0.0, 2026-06 +11.4, 2026-07 +13.7, 2026-08 -0.1, 2026-09 +6.6, 2026-10 +18.4 |
| S03 | 一年窗非零变动点 / 前 45 天内有日央行决议实录者 | series_store.JP_POLICY_RATE;release_calendar JP_POLICY_TARGET | 8 个:2025-12-01 +7.9, 2026-01-01 +17.1, 2026-04-01 -0.1, 2026-06-01 +11.4, 2026-07-01 +13.7, 2026-08-01 -0.1, 2026-09-01 +6.6, 2026-10-01 +18.4;有实录: 2026-10-01(决议 2026-09-18) |
| S04 | 合成交叉盘(EURUSD×USDJPY)与两腿;窗两端可见政策水平差(MRO−日本月均) | series_store.EURUSD × series_store.USDJPY; series_store.ECB_MRO; series_store.JP_POLICY_RATE | 六个月窗起点(2026-05-23 当日或之前的最近共同观测日) 2026-05-22;交叉盘: 2026-05-22=184.7972, 2026-08-20=184.7681, 2026-09-15=178.2921, 2026-09-16=179.1400, 2026-10-23=175.6091, 2026-11-20=175.1941, 2026-11-23=174.3212;变动%: 2026-05-22→2026-11-20 -5.20, 2026-08-20→2026-11-20 -5.18, 2026-05-22→2026-09-15 -3.52, 2026-09-16→2026-11-20 -2.20, 2026-05-22→2026-10-23 -4.97, 2026-10-23→2026-11-20 -0.24;腿 2026-05-22→11-20: EURUSD -5.6056%、USDJPY +0.4333%;政策水平差: 2026-05-22: MRO 2.15(观测 2025-06-11)−月均 0.727(观测 2026-05-01)=1.423 个百分点; 2026-11-20: MRO 2.65(观测 2026-09-16)−月均 1.227(观测 2026-10-01)=1.423 个百分点 |
| S10 | 对质环 1 各『变更前可见读数』相对 2026-02 的差;2026-05 峰值与第二次决议日前读数之差 | series_store.EA_HICP_YOY @2026-02/2026-04/2026-05/2026-07/2026-08 | 2026-04 +1.1, 2026-05 +1.3, 2026-07 +1.0, 2026-08 +1.3;峰值差 0.3 |
| S05 | 美元端政策利率(同口径)与市场收益率末观测 | series_store.DFEDTARL/DFEDTARU/UST_10Y | DFEDTARL@2026-11-23=3.75; DFEDTARU@2026-11-23=4.0; UST_10Y@2026-11-19=5.04 |
| S07 | VIX 月窗幅度的存储精度与显示精度 | series_store.VIX @2026-10-23/@2026-11-20 | +84.5244% / +84.5244% |
| S08 | JP_CPI_YOY 全序列最高 | series_store.JP_CPI_YOY | 2023-01=4.31 |
| S09 | 读者报告行号核对 | MAP_REPORT.md / FULL_REPORT.md / report.md | {"MAP": {"见裁定理由": [136], "2026-11-05": [42, 198], "同轮事件并项": [167], "STALE": []}, "FULL": {"seat_invoked=False": [180], "STALE": []}, "report.md STALE": 0} |
| S06 | 注册表口径文字 | metric_registry.ECB_MRO/ECB_DFR.freshness.decision_dated_note;EA_HICP_YOY.release_semantics | 见第 4 节 M-1、M-5 原文引用 |

## 2. 六查逐项结论

### C1-INFL-DIVERGE(两地通胀同比方向相反)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关。日本全国 CPI 同比、欧元区 HICP 同比 2026-10 与 2025-10 的同月观测在序列面(C001–C006);东京序列起点 2026-01、2025-10 无观测(C007/C008)。 |
| 支持度 | 完全支持。2.44−2.99=−0.55、4.0−2.1=+1.9;『低于/高于』方向词与数值一致(C009/C010);走位与点值格同值(B001–B036);陈述层中文数字逐句直算(CN001–CN007)。 |
| 竞争解释(真正竞争) | 『能源与进口传导+高基数消退→剪刀差收敛』与『需求与政策组合→持续分化』对后续路径预期相反,是真竞争;均标【假设】,并以『引擎无分项构成与需求面序列』如实并列(K011),当前不可区分。 |
| 反对证据 | 『日本回落』只对去年同月成立: 近 12 个月中其余 11 个月里 10 个月读数低于最新值,较 1/3/6 个月前为 +0.28/+0.47/+1.06(反方攻击 1);基期 2025-10=2.99 为当时局部小高点(G008/G009/G012)。与陈述不相左(限定『相比去年同月』,走位写『此后总体回升』)。2025基/2020基拼接口径对 −0.55 的影响在只读面不可量化,注册表拼接告警阈 0.10pp(反方攻击 2)。 |
| 结论是否超出证据 | 未超出。只述方向与差值;东京端基期缺席写『同比对照不可判』,未补数。 |
| 证伪条件可观测性 | 即期对照无未来条件;后续路径由情景 S1/S2 承担(见情景六查)。 |

### C2-POLICY-SYNC(同向收紧、可核行动均已生效)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关。ECB_MRO/ECB_DFR 变更点、日央行两条实录、JP_POLICY_RATE 月均(D001–D040)。 |
| 支持度 | 欧央行两次 +25bp(2026-06-17、2026-09-16)、MRO 2.65/DFR 2.5、决议日回推(06-11、09-10)、间隔 91 天全中;日央行 2026-09-18 决议/09-24 生效/10-30 维持、24 天全中;月均 0.478→1.227、锚 0.727/1.227、一年窗净变动与变动点之和 75bp 全中(D034/D035);读者报告政策表日本行『距上次调整(按生效日)/距决议/距维持』60/66/24 天与直算一致(D026)。 |
| 竞争解释(真正竞争) | 『读数驱动』与『正常化程序与汇率/金融稳定考量』对决议节奏预期不同,是真竞争;月频证据且无央行表态文本序列(K012),不可区分,如实并列。 |
| 反对证据 | (i) 欧央行 2026-09-16 后 68 天决议面不可见(由 C3 专门处理);(ii) 日央行实录无前值字段,『收紧』方向只有市场口径间接证据(N010;反方攻击 5);(iii) JP_POLICY_RATE 一年窗 6 个变动点(阈值口径;计入两次 -0.1bp 微降则为 8 个非零台阶)中,仅 2026-10-01 一点前 45 天内有日央行决议实录(G018;补充计算 S03)——判断档写『其余月均台阶在发布日历无对应实录,不作相容性判断』,与之一致。 |
| 结论是否超出证据 | 『无未生效决议』限定于引擎记录面并带【尚未验证】(N002/N003);总判断未把月均写成官方目标(N008)。总判断句日本端方向未带【推断】(MINOR M-4)。 |
| 证伪条件可观测性 | 『其后决议面』待日历补录或官网可核——可观测,当前面缺席已披露。 |

### C3-ECB-VISIBILITY(欧央行序列可见性)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关。序列末观测、注册表新鲜度阈、Gate A 名单、L1 质量位、日历零条(D014–D019,K007–K009,N005)。 |
| 支持度 | 全部属实: 68 天>10 天;degraded 名单含两序列;L1 DEGRADED×2;日历零 ECB 条目;陈述层中文数字逐句直算(CN015–CN017)。 |
| 竞争解释(真正竞争) | 『源端未再更新(实际无新决议)』与『断档期间有新决议』对现值水平预期相反,是真竞争;引擎面不可区分、须官网核对并标『引擎外补充待授权』——处置恰当。 |
| 反对证据 | 注册表同处的决策驱动口径(无更晚已证实决议不作过期)与引擎点值格 status=ok/freshness_basis=policy_confirmation(O009/O010),即引擎并未把现值判为过期——与 degraded 并存的另一面,席位未并列(MINOR M-1)。 |
| 结论是否超出证据 | 未超出。『不可判【尚未验证】』『仅覆盖引擎可见面』;事实位零句把 09-16 后状态写成『无变化/维持』(N001,反方攻击 6)。 |
| 证伪条件可观测性 | 可观测(官网或日历补录后即可核)。 |

### M1 环 1(通胀路径,E1)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关(G001–G011,F019–F032)。 |
| 支持度 | 判断档全部月度路径点值对 34 对(欧元区 10、日本全国 14、东京 2、政策月均 8)逐对复核全中;『两度小幅回升』『总体回升』用词与逐月环比一致(G012/G013)。 |
| 竞争解释(真正竞争) | 事实环,无需;隐含的因果解读由对质环 1 承担。 |
| 反对证据 | 无(路径直读)。 |
| 结论是否超出证据 | 未超出;E1 环只含事实与【推断】标注(G021)。 |
| 证伪条件可观测性 | 不适用(事实环)。用词『2025-01 高点』为局部高点(NIT N-1)。 |

### M1 环 2(政策面跟进,E1)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关(G014–G018,D005–D008)。 |
| 支持度 | 变更点、幅度、日期全中;决议日逐处标【推断】(G017);BOJ 月均台阶只对 2026-09→10 作相容判断,其余不作(G018)。 |
| 竞争解释(真正竞争) | 『跟进』隐含的因果由对质环 1 承担(读数驱动 vs 程序驱动)。 |
| 反对证据 | 两序列维持 2.15/2.0 共 371 天期间读数已由 1.7 升至 3.0 未触发变更(G096–G098)——席位已在裁定理由并列(反方攻击 8)。 |
| 结论是否超出证据 | 未超出。 |
| 证伪条件可观测性 | 由对质环 1 承担: 区分指标 EA_HICP_YOY 在场(G102),两解释对其上的预期不同(决议前可见抬升 vs 无稳定先后关系),n=2(G100),裁『尚不能区分』。 |

### M1 环 3(汇率传导,E2)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关(G022–G043,K010)。 |
| 支持度 | 观察事实全中: EURUSD −2.24%、USDJPY +2.05%、DXY +1.96%;盘中 −2.51%/+1.82%/+2.23%;合成交叉盘 −0.24%/−0.73%;裁定理由所称『两解释预期未分立』经复算成立(见竞争解释一栏)。 |
| 竞争解释(真正竞争) | 『美元全局因素与风险情绪主导』对『政策利差主导』: 既述预期为同向 vs 方向分立,是真竞争;纳入美元端利率后两者对本月窗预期相同(预期未分立),按读者报告判断口径属『诚实缺省』。 |
| 反对证据 | 美元端利率更高使主解释预期反转(席位自列);UST_10Y 口径不对等(MINOR M-2);更长窗读数: 合成交叉盘 2026-05-22→2026-11-20 为 -5.20%,同期可见的两地政策水平差 1.423→1.423 个百分点未变,与『利差主导』不相容(反方攻击 9);判断档只检验了本月窗,六个月窗读数未并列(MINOR M-7)。 |
| 结论是否超出证据 | 未超出(『幅度小,利差渠道未获检验亦未被否定』限本月窗;六个月窗读数未并列见 MINOR M-7)。 |
| 证伪条件可观测性 | 区分指标 EURUSD 在场(G103);窗内无政策变动点(G101),本月窗无检验力,如实。 |

### M1 环 4(资产面,E2)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关(G045–G087,L002/L003)。 |
| 支持度 | 数值全中: SPX −9.36%、NIKKEI225 −9.98%、DAX −1.50%、CAC40 +1.86%;VIX 19.45→35.89(+84.5%);末六日路径;跳升窗四地;距政策日 14/58/21/65 天;发布日 VIX +18.70%/+26.20%;两日汇市单日变动≤0.23%。 |
| 竞争解释(真正竞争) | 『紧缩+通胀粘性』与『全局风险/流动性冲击』对 VIX 路径与区域相对表现预期不同,是真竞争;席位另列读数发布与会议纪要为候选驱动。 |
| 反对证据 | 主解释两项派生预期未获支持(欧元区股指不弱于美股;VIX 跳升不与政策日历对齐),席位已自列;发布日单日读数未列(MINOR M-6,反方攻击 10)。 |
| 结论是否超出证据 | 未超出(『单一归因于两地政策不可证』)。 |
| 证伪条件可观测性 | 区分指标 VIX 在场(G104);『待 2026-11-23 收盘及其后收盘数据复检』可执行。 |

### 情景 S1/S2 与历史类比

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关(I001–I017,H001–H007)。 |
| 支持度 | 前提与截止日读数相容(EA 4.0/JP 2.44/VIX 2026-11-20 收盘 35.89 落在两情景之间,未决);类比能力已执行(扫描 1871/有效 74/TOP1 2025-03 距离 0.727),历史 0 段。 |
| 竞争解释(真正竞争) | 两情景方向互补(维持 3.5% 以上 vs 回落至 3.0% 以下;日本端 2.0% 对应);历史类比不适用。 |
| 反对证据 | S2 与近一月观察相反,席位自标『并列反例情景』;历史类比不适用。 |
| 结论是否超出证据 | 未超出(标『假设·非预测』;零段注记,候选月仅出现于注记,无事后结果数字)。 |
| 证伪条件可观测性 | 指标在册可观测;时限 2027-02-15 晚于 2026-12 观测月入档;3.0%–3.5% 中间区间如实;欧央行政策分量不可数值核验已披露(I012)。S1 置信档用词见 NIT N-4。 |

### 总判断/走位/对质表一致性(⑩)

| 查项 | 结论 |
|---|---|
| 证据相关性 | 相关(J001–J024)。 |
| 支持度 | 总判断与读者报告逐字一致(J022);走位 2/2 在场(J016);对质表结构字段 18/18 在场(J017);裁定三处均『尚不能区分』,与质量门注记[1]自述『支持主解释 0·支持竞争解释 0·尚不能区分 3』一致(J002/J003);总判断政策水平与 C2 一致(J012);L3 20 条引用全解析(J004–J006)。 |
| 竞争解释(真正竞争) | 各处均已并列主/竞争预期。 |
| 反对证据 | 裁定理由(verdict_note)与三转折叙述未渲染(范围外观察 S-1/S-2)。 |
| 结论是否超出证据 | 未超出;三处均未把『尚不能区分』写成倾向性结论(对质环 3 的倾向只写在理由里,NIT N-3)。 |
| 证伪条件可观测性 | 三处区分指标(EA_HICP_YOY/EURUSD/VIX)均在证据索引(G102–G104)。 |

## 3. 反方攻击记录

每条 L3 矛盾陈述、机制链每一环至少一条;攻击用的计算见 counterexamples.json(s20_counter.py)与第 1.4 节补充计算。

- 反方攻击 1: [C1] 换比较基期看方向是否翻转 → 日本全国 CPI 同比较 1/3/6 个月前为 +0.28/+0.47/+1.06,仅同比口径为 -0.55;近 12 个月中 10 个月读数低于最新值(欧元区同法 +0.2/+1.1/+1.0/+1.9,11 个月全部低于最新值)。陈述以『相比去年同月』限定并写『此后总体回升』→ 不推翻,记 NIT N-9
- 反方攻击 2: [C1] 2025基/2020基拼接口径是否足以翻转 -0.55 → 注册表 JP_CPI_YOY.calc 的拼接告警阈 0.10pp 约为差值的 1/5;重叠期双基值不在只读面,未能独立量化 → 不推翻(残留不可量化项如实记录)
- 反方攻击 3: [C1] 东京 CPI 基期缺席是否被绕过 → 序列起点 2026-01,2025-10 无观测;席位写『同比对照不可判』并披露 Gate A noncore_missing → 诚实缺席成立
- 反方攻击 4: [C2] 若 2026-09-16 后欧央行另有决议则『无未生效决议』为假 → 引擎面序列止于 09-16、日历零条 ECB 实录,该情形在只读面既不可证也不可否;席位把结论限定于『引擎记录面』并标【尚未验证】→ 不推翻
- 反方攻击 5: [C2] 日本端『收紧』方向是否只有间接证据 → 日央行实录无前值字段;月均 12 个逐月台阶中仅 2 次 -0.1bp 微降、净 +75bp,2026-09 +6.6bp(决议 09-18、生效 09-24,月内生效 7 天)→2026-10 +18.4bp 与上调相容 → 方向有市场口径证据,【推断】标注恰当;总判断句未带标注记 MINOR M-4
- 反方攻击 6: [C3] 席位是否把 degraded 序列冒充现行值 → 全文分句扫描: 事实位零句把 2026-09-16 后状态写成『无变化/维持』,5 处『维持』类命中均为情景/竞争解释/带『不可见·不可判·尚未验证』限定句 → 攻击不成立;注册表决策驱动口径未并列记 MINOR M-1
- 反方攻击 7: [M1 环 1] 路径数字逐月核对 → 判断档全部月度路径点值对 34 对(欧元区 10、日本全国 14、东京 2、政策月均 8)全部与序列面一致;『2025-01 高点』全序列最高为 4.31@2023-01 → 数值全中,用词记 NIT N-1
- 反方攻击 8: [M1 环 2] 若读数驱动,2026-01→04 读数 1.7→3.0 时欧央行应已上调 → 实际维持 2.15/2.0 共 371 天未动;席位已在裁定理由并列该反向观察,n=2 裁『尚不能区分』→ 不推翻
- 反方攻击 9: [M1 环 3] 用问句窗六个月的交叉盘能否检验利差渠道 → 合成 EURJPY 2026-05-22→2026-11-20 为 -5.20%(腿: EURUSD -5.61%/USDJPY +0.43%);同期欧央行两度上调合计 +50bp,日本端月均亦由 0.727 升至 1.227,可见的两地政策水平差(MRO−日本月均)1.423→1.423 个百分点未变 → 与『利差主导』不相容,但美元全局主导解释对两腿分立亦无预期;席位只对本月窗(-0.24%/-0.73%)下结论 → 不推翻裁定;六个月窗读数未并列记 MINOR M-7,口径与渲染问题记 MINOR M-2
- 反方攻击 10: [M1 环 4] 发布日单日读数是否支持『读数发布主因』 → 2026-11-20 NIKKEI225 -5.06% 深于 SPX -3.70%(窗内四地最大单日跌幅),2026-11-16 欧元区股指跌幅浅于美股(DAX -0.57%、CAC40 -0.20% vs SPX -1.92%);全局同跌、单日读数不具区分力 → 不推翻结论,记 MINOR M-6
- 反方攻击 11: [情景] 证伪条件是否可观测、是否已被截止日数据判定 → EA_HICP_YOY/JP_CPI_YOY/VIX 在册且持续更新;截止日读数 EA 4.0/JP 2.44/VIX 2026-11-20 收盘 35.89 落在两情景之间(未决);时限 2027-02-15 晚于 2026-12 观测月入档(2027-01) → 可观测、未触发
- 反方攻击 12: [历史类比] 零段是否被偷引事后结果 → 候选月 2025-03 仅出现于零段注记,全文无『随后 N 个月』结果数字 → 成立
- 反方攻击 13: [总判断] 读者报告与判断档是否一致 → 总判断逐字在场;走位 2/2、对质表结构字段 18/18 在场;对质裁定三处均『尚不能区分』,与质量门注记[1]自述『支持主解释 0·支持竞争解释 0·尚不能区分 3』一致 → 一致
- 反方攻击 14: [M1 环 4 数字] VIX 月窗 +84.5% 按显示精度与存储精度分别复算 → 19.45→35.89 两种精度均为 +84.52%,报告取一位小数 +84.5% → 命中

## 4. 问题清单

### MAJOR(0 条)

未发现数字/日期/方向错或与证据相左、缺基期给同比、相邻口径冒充、事后信息冒充当时可知、无标注的超出证据结论、不可观测的证伪条件。逐项排除依据见第 2 节六查与第 3 节反方攻击。

### MINOR(7 条,口径/披露可改进,不改变结论)

**M-1** — 位置: agent_judgment.json l3.contradictions[2].statement(C3-ECB-VISIBILITY);reader_map.regions[0].from_to(欧元区走位);quality_gate_notes[4]

- 原句: 「观测日距研究截止 2026-11-23 六十八天,超过注册表新鲜度阈十天,当日快照 Gate A 两序列列于 degraded 名单,L1 事实行 quality_status=DEGRADED」
- 问题: 欧央行序列时效只并列了一半口径:只引滞后口径(68 天>注册表 10 天阈→Gate A degraded/L1 DEGRADED,均属实),未并列注册表同处的决策驱动口径(metric_registry ECB_MRO/ECB_DFR.freshness.decision_dated_note:『决策驱动政策目标序列——观测日=政策最后确认/变更日;无更晚已证实决议不作过期(利率长期不变≠数据停更),有已证实更晚决议而未反映=确证过期』)与引擎点值格状态(status=ok,freshness_basis=policy_confirmation)。结论『其后是否有新决议不可判【尚未验证】』与决策驱动口径相容且偏保守,不构成数字/日期/方向错;属披露可改进(复算行 O009/O010)。
- 建议改句(数字均有复算行或补充计算支撑): 「在该句后补:『注册表对两序列另注决策驱动口径(观测日=政策最后确认/变更日,无更晚已证实决议不作过期),引擎点值格据此标 ok——两面口径并存,本档不以 degraded 推断有新决议,亦不以现值推断无新决议。』」

**M-2** — 位置: l3.mechanism_chains[0].links[2].text(M1 第 3 环);reader_map.transmission[0].links[1].causal_hypothesis 与 verdict_note(对质环 2)

- 原句: 「但该预期未纳入美元端利率(UST_10Y 最新 5.04%,高于 MRO 2.65% 与 BOJ 目标约 1.25%)」
- 问题: 两点口径问题。(i) 以 10 年期美债收益率(市场收益率口径)充当『美元端利率』与两地政策目标利率比较,口径不对等;同口径的联邦基金目标区间 3.75%–4.00%(DFEDTARL/DFEDTARU 2026-11-23 观测)只写在 verdict_note。(ii) 主解释的既述预期是『方向分立』,本月窗观测为同向;席位以『未纳入美元端利率』这一辅助前提把主解释改写成与竞争解释同向,于是本行在本月窗对两解释无检验力(窗内三地无政策利率变动点,G101)——如实,但支撑这一读法的裁定理由在三件读者报告中均未渲染(范围外观察 S-1),读者报告第 136 行『见裁定理由』成悬空指引,读者只见到对质表上『方向分立』的预期与『尚不能区分』的判断并置。定性论证在政策利率口径下同样成立(3.75–4.00 亦高于 2.65 与约 1.25),结论不变(复算行 D031/E016/G103)。
- 建议改句(数字均有复算行或补充计算支撑): 「但该预期未纳入美元端利率(快照序列面联邦基金目标区间 3.75%–4.00%,DFEDTARL/DFEDTARU 2026-11-23 观测,不在本轮证据索引;UST_10Y 最新 5.04% 为市场收益率口径),美元端政策利率亦高于 MRO 2.65% 与 BOJ 目标约 1.25%;本月窗两解释预期相同、无检验力」

**M-3** — 位置: l3.contradictions[0].statement(C1);reader_map.regions[0].from_to;reader_map.headline_conclusion

- 原句: 「欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16,引擎推定规则、非日历实录)」
- 问题: 问句明问『各数据的公布时间』。2026-11-16 是引擎推定规则(月末+16 天)给出的日期,注册表 release_semantics 亦写『Eurostat月度HICP(次月中旬终值)』——即该日对应终值档;冻结日历所载 EA HICP 三条实录均为两档形态(次月首日快报+月中终值: 2021-06-01/2021-06-17、2022-07-01/2022-07-19、2025-04-01/2025-04-16),据此 2026-10 读数的首发应早于 11-16。席位已标『引擎推定规则、非日历实录』并在对质环 1 裁定理由使用了两档形态(复算行 A026/G093/G094),但未在数据面与走位并列首发档。不构成日期错;属披露可改进。
- 建议改句(数字均有复算行或补充计算支撑): 「…发布 2026-11-16 为引擎推定规则下的终值日;按冻结日历所载 EA HICP 实录的两档形态(次月首日快报+月中终值),2026-10 读数首发应早于此日,非日历实录」

**M-4** — 位置: reader_map.headline_conclusion;reader_map.regions[1].from_to(日本走位)

- 原句: 「两地政策利率同向收紧——日本央行政策目标 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持;发布日历实录)」
- 问题: 日央行实录无前值字段,『收紧』方向系由月均市场利率台阶推得;C2 正文已标【推断】、走位写明『月均≠宣布值』,总判断句对日本端方向未带【推断】。方向有市场口径证据(近 12 个月月均 0.478→1.227,净 +75bp,12 个逐月台阶中仅 2 次 -0.1bp 的微降;2026-09 +6.6bp、2026-10 +18.4bp 与 2026-09-24 生效的上调相容;补充计算 S03),不构成方向错;属四层标注在总判断句的缺口(复算行 N007/N008/N009/N010)。
- 建议改句(数字均有复算行或补充计算支撑): 「两地政策利率同向收紧——日本端方向为【推断】(实录无前值,依据月均市场利率台阶 0.478→1.227): 日本央行政策目标约 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持;发布日历实录)」

**M-5** — 位置: reader_map.transmission[0].links[0].main_predicts 与 verdict_note(对质环 1)

- 原句: 「决议日(回推 2026-06-11)前可见 2026-04=3.0、生效日前可见 2026-05=3.2」
- 问题: 『决议日前可见读数』的数值取自快照最新修订值(引擎点值格 vintage_semantics=『事后回顾(最新修订值,非当时首发值)』;注册表 EA_HICP_YOY.release_semantics:『HICP流程对近月含回溯修订(2025-12 值1.9→2.0)…revision_semantics=latest_vintage_asof_collected』),未并列首发值口径。样本 n=2、结论为尚不能区分;『两次变更前读数均高于 2026-02 的 1.9』在决议日前/生效日前两口径下的差距为 1.1、1.3、1.0、1.3 个百分点,0.1pp 级修订不翻转;『第二次决议日前 2.9 低于 2026-05 峰值 3.2』一条差距 0.3 个百分点,对同量级的修订敏感,但席位已自注该条对发布形态敏感(按冻结日历两档形态计则此条不成立)。属披露可改进(复算行 O014、G088–G099;补充计算 S10)。
- 建议改句(数字均有复算行或补充计算支撑): 「决议日(回推 2026-06-11)前可见 2026-04=3.0、生效日前可见 2026-05=3.2(读数为快照最新修订值,非当时首发值;修订量级参见注册表所举 0.1pp 例)」

**M-6** — 位置: l3.mechanism_chains[0].links[3].text(M1 第 4 环);reader_map.transmission[0].links[2].verdict_note(对质环 3)

- 原句: 「读数发布主因未获跨地区支持」
- 问题: 所据两点均属实:跳升窗(2026-11-13→2026-11-20)内累计跌幅四地均不深于美股(SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%),两日欧元、日元对美元单日变动≤0.23%(最大 -0.2293%)。但未列发布日单日读数: 2026-11-20(日本 CPI 推定发布日)NIKKEI225 -5.06% 深于 SPX -3.70%、DAX -2.60%、CAC40 -1.89%,为窗内四地最大单日跌幅;2026-11-16(欧元区 HICP 推定发布日)欧元区股指跌幅浅于美股(DAX -0.57%、CAC40 -0.20% vs SPX -1.92%)。单日读数与全球同跌相容,既不确证也不否定发布主因;『单一归因于两地政策不可证』的结论不变。属反对证据未并列(反方攻击 10;补充计算 S01)。
- 建议改句(数字均有复算行或补充计算支撑): 「读数发布主因未获跨地区支持(按跳升窗内累计跌幅判读;单日看 2026-11-20 NIKKEI225 -5.06% 深于 SPX -3.70%,为窗内四地最大单日跌幅,与全局冲击相容,不足以区分发布主因与全局冲击)」

**M-7** — 位置: l3.mechanism_chains[0].links[2].text(M1 第 3 环);reader_map.transmission[0].links[1].verdict_note(对质环 2)

- 原句: 「幅度小,利差渠道未获检验亦未被否定」
- 问题: 汇率面的检验只用一个月窗(窗起 2026-10-23),席位自注『仅一个月窗』;问句窗为最近六个月(2026-05-23 起)。本席补算: 取 2026-05-23 当日或之前的最近共同观测日 2026-05-22 为起点,合成 EURJPY(EURUSD×USDJPY)由 184.7972 降至 2026-11-20 的 175.1941(-5.20%;腿: EURUSD -5.61%、USDJPY +0.43%),同期可见的两地政策水平差(MRO−日本月均)为 1.423→1.423 个百分点(2.15−0.727 → 2.65−1.227),未变。利差假说在水平差未变时对交叉盘无趋势性预期,该读数与『利差主导』不相容;美元全局主导解释对两腿分立亦无预期——不改变『尚不能区分』,但『未被否定』只在本月窗内成立,宜并列六个月窗读数(反方攻击 9;补充计算 S04)。
- 建议改句(数字均有复算行或补充计算支撑): 「幅度小;本月窗利差渠道未获检验亦未被否定。六个月窗(2026-05-22→2026-11-20)合成交叉盘 -5.20%,同期可见的两地政策水平差 1.423→1.423 个百分点未变——利差渠道在六个月窗内与交叉盘读数不相容,但两种解释对该读数均无预期,仍不构成检验」

### NIT(9 条,行文)

- **N-1** — 位置: l3.mechanism_chains[0].links[0].text(M1 第 1 环);reader_map.regions[1].from_to
  - 原句: 「自 2025-01 高点 4.03 回落」
  - 说明: 该点为近一年/局部高点(全序列最高 4.31@2023-01),宜写『近一年高点』(复算行 G006;补充计算 S08)。
  - 建议: 「自 2025-01 的近一年高点 4.03 回落」
- **N-2** — 位置: reader_map.headline_conclusion;reader_map.regions[1].from_to(日本走位);l3.mechanism_chains[0].links[2].missing_link_note(『BOJ 目标 1.25%』)
  - 原句: 「日本央行政策目标 1.25%」
  - 说明: 发布日历两条日央行实录注记均为『约1.25%』,C2 陈述作『约一点二五』,情景文字作『目标现约 1.25%』/『目标约 1.25%』;总判断与走位省『约』(复算行 N011)。
  - 建议: 「日本央行政策目标约 1.25%」
- **N-3** — 位置: reader_map.transmission[0].links[2].verdict_note 与 face_off_verdict(对质环 3)
  - 原句: 「证据倾向竞争解释但不足以裁定,尚不能区分」
  - 说明: 裁定词『尚不能区分』较其裁定理由(明写证据倾向竞争解释)保守;因第三类候选驱动(会议纪要发布)在场且该对质不裁、竞争解释『快速回落』预期仅有一个盘中观测,保守可接受;宜在渲染字段带倾向注记,理由文本身未渲染(范围外观察 S-1)。
  - 建议: 「证据倾向竞争解释(会议纪要发布属第三类候选驱动、本对质不裁;『快速回落』预期仅有一个盘中观测)但不足以裁定,尚不能区分;渲染字段作『尚不能区分(证据略倾向竞争解释)』」
- **N-4** — 位置: l4.scenarios[0].rows.asset_direction.confidence_tier
  - 原句: 「有相关证据」
  - 说明: 所引为月窗观察(NIKKEI225@2026-11-20、VIX@2026-11-23),其归因席位自判未定;『相关』成立但不构成支持性证据(复算行 I013)。
  - 建议: 「方向相容(归因未定)」
- **N-5** — 位置: reader_map.turnings[1].follow_or_diverge(转折 2)
  - 原句: 「跟进方向一致,月频先后未定」
  - 说明: 生效日 2026-06-17 晚于转折段终点月 2026-05,先后已定;『先后未定』只指读数可见性与决议时点,措辞可更精确(复算行 F034)。
  - 建议: 「生效日 2026-06-17 晚于转折段终点,跟进方向一致;读数可见性与决议时点的先后未定」
- **N-6** — 位置: l3.contradictions[0].statement;reader_map.regions[1].from_to(东京都 CPI)
  - 原句: 「点值取自快照序列面、L1 无对应事实行」
  - 说明: Gate A noncore_missing 序列的两点值作为契约锚回声进入 C1 与日本走位,状态已在原处披露且未进入总判断;宜加『参考值』字样(复算行 K001–K003)。
  - 建议: 「…点值取自快照序列面、仅作参考,L1 无对应事实行」
- **N-7** — 位置: l3.contradictions[1].statement(C2);quality_gate_notes[4]
  - 原句: 「市场口径无担保隔夜拆借利率(月均,JP_POLICY_RATE)最新一期报 1.227%」
  - 说明: 该序列 L1 quality_status=WARN(发布时间未验证)及其推定发布日 2026-11-05(读者报告第 42 行有)未进入判断档正文;C1 只并列了两条通胀序列的 WARN(复算行 A020/K005/K006;补充计算 S09)。
  - 建议: 「…最新一期报 1.227%(观测月 2026-10,推定发布日 2026-11-05,L1 quality_status=WARN: 发布时间未验证)」
- **N-8** — 位置: quality_gate_notes[5] 第②项
  - 原句: 「本档陈述层对无别名指标的数值一律用中文数字表述」
  - 说明: 成立于三条矛盾陈述正文;竞争解释、走位、机制链、对质表仍用阿拉伯数字(契约因此未逐位核验),本席已在 ⑦⑩ 逐数复算全中;自述宜写明仅限矛盾陈述正文(复算行 O007/O008)。
  - 建议: 「本档三条矛盾陈述正文对无别名指标的数值一律用中文数字表述」
- **N-9** — 位置: l3.contradictions[0].statement(C1)
  - 原句: 「回落约零点五五个百分点」
  - 说明: 同比回落只对去年同月成立: 近 12 个月中其余 11 个月里有 10 个月读数低于最新值,较 1/3/6 个月前为 +0.28/+0.47/+1.06;走位已有『此后总体回升』,可在 C1 补半句免读者误读为趋势下行(反方攻击 1;补充计算 S02)。
  - 建议: 「回落约零点五五个百分点(仅就去年同月基期而言;较六个月前则回升约一点零六个百分点)」

### 披露后可接受、不列为问题的点

- 欧央行两序列在 Gate A 为 degraded、L1 为 DEGRADED 的情况下被用作「最新生效水平」: 问句所问正是现行目标利率,席位把结论限定于引擎记录面/可见面并标【尚未验证】,且事实位没有任何一句把 2026-09-16 之后写成「无变化/维持」(N001–N005)。
- 情景的欧央行政策分量不设数值触发: 数值证伪指标(EA_HICP_YOY/JP_CPI_YOY/VIX)在册可观测;政策分量以决议实录核验并明写「冻结日历对欧央行零条实录,须待日历补录」,属如实披露而非不可观测(I012)。
- 对质环 2 裁定「尚不能区分」: 主解释经辅助前提(美元端利率)后与竞争解释在本月窗预期相同,按读者报告判断口径(「预期未分立=尚不能区分,诚实缺省」)成立;口径与渲染问题见 M-2,六个月窗读数见 M-7。
- 对质环 3 裁定「尚不能区分」而理由写「证据倾向竞争解释」: 第三类候选驱动在场、回落观测只有一个盘中点,保守裁定可成立(NIT N-3 只提行文)。
- 东京都 CPI(Gate A noncore_missing)两点值进入 C1 与日本走位: 系契约要求的锚回声,状态在原处披露,未进入总判断(NIT N-6)。

## 5. 范围外观察(引擎渲染/口径面,供操作者;非判断偏离)

- **S-1**(J017X): 传导对质三环的裁定理由(verdict_note)在 MAP_REPORT.md、FULL_REPORT.md、report.md 均未渲染;MAP_REPORT.md 第 136 行「该预期未纳入美元端利率——见裁定理由」因此成为悬空指引(读者在读者报告里看不到美元端利率高于两地这一关键理由,也看不到对质环 3 的证据倾向)。
- **S-2**(J018X): 三转折的叙述(narrative,含逐月路径与「其余月均台阶不作相容性判断」)三件均未渲染;读者报告「过去一年的三个转折」表(第 163–168 行)按并项口径把转折 1 与转折 2 并成一行(第 167 行「同轮事件并项」;第 170 行有并项说明: 同维度且观测窗重叠的转折视为同一轮事件),表内两行——并项后的行把两段「跟进/背离」文字用分号拼接,逐转折的对应关系须对照判断档才可分。
- **S-3**(J020): 质量门注记六条(含引擎缺口四项的自述)三件均未渲染。
- **S-4**(K015): 引擎点值格对 Gate A noncore_missing 的 JP_CPI_TOKYO_YOY 两个锚仍标 status=ok,读者报告环境表与覆盖表该行亦标 ok,与同页「缺席/降级数据不得进入研究结论」并置。
- **S-5**(O013): 引擎面对欧央行决议日有两种表述——注册表 calc/release_semantics 写「决议变更即时生效/决议公布后生效并当日更新系列」,读者报告覆盖表把 2026-09-16 写作「ECB 决议日当日公布(变更日观测)」,政策表却写决议 2026-09-10、生效 2026-09-16。席位取政策表面并把决议日标【推断】,生效日 2026-09-16 在两种读法下不变。
- 另记(未单列复算行,阅读三件报告时所见): 契约核验的 STALE 位未在读者报告露出(S09:三件均无「STALE」字样;FULL_REPORT.md 第 180 行为 `review: required=True seat_invoked=False verdict=None`,系本席成文前的应有状态);三件读者报告对判断档各段互补渲染(总判断只在 MAP_REPORT.md,机制链四环全文只在 FULL_REPORT.md/report.md),除上列 S-1–S-3 外无任何判断段落三件均缺席。

## 6. 裁决

范围内复算 396 点全部命中、偏离 0;十五类覆盖齐备;六查各项无「结论超出证据且无标注」「事后信息冒充当时可知」「证伪条件不可观测」;14 条反方攻击均未推翻判断档的任何数字、日期或方向。所列 7 条 MINOR 均为口径并列与披露完整性的改进项,不改变任何结论;无 REVISE 级问题。

**裁决: UPHELD**(must_fix 为空;MINOR/NIT 如实列出,供研判席下一轮参考,不作为放行条件)。

