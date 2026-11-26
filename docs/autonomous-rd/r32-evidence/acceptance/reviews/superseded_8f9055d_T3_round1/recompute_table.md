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
