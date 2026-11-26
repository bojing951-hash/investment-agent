| 编号 | 覆盖项 | 受审位置 | 受审原文片段 | 出处(文件+键) | 直算值 | 报告值 | 一致 |
|---|---|---|---|---|---|---|---|
| P001 | ①研究截止日 | C2 | 截至研究截止 2026-11-23 | report.json research_plan.point_anchors[最新一期].as_of | "2026-11-23" | "2026-11-23" | 是 |
| P002 | ①研究截止日 | C3 | 距研究截止 2026-11-23 六十八天 | report.json research_plan.point_anchors[最新一期].as_of | "2026-11-23" | "2026-11-23" | 是 |
| P003 | ①研究截止日 | Q4 | 研究截止日=2026-11-23(快照版本日 | report.json research_plan.point_anchors[最新一期].as_of | "2026-11-23" | "2026-11-23" | 是 |
| P004 | ①研究截止日 | Q4 | 快照采集于 2026-11-23T22:53:47+08:00 | 快照 顶层键 research_as_of | "2026-11-23T22:53:47+08:00" | "2026-11-23T22:53:47+08:00" | 是 |
| P005 | ①研究截止日 | Q4 | 研究截止日=2026-11-23(快照版本日 | 快照 顶层键 target_date(规范化 YYYYMMDD) | "20261123" | "20261123" | 是 |
| P006 | ①研究截止日 | C2 | 最近六个月(2026-05-23..2026-11-23) | report.json research_plan.question_window.windows[0].from/to | ["2026-05-23", "2026-11-23"] | ["2026-05-23", "2026-11-23"] | 是 |
| P007 | ①研究截止日 | C2 | 最近六个月(2026-05-23..2026-11-23) | 独立推算: 截止日−6个自然月 | "2026-05-23" | "2026-05-23" | 是 |
| P008 | ①研究截止日 | M1.step3 | 并列问句窗六个月(2026-05-22 收盘→2026-11-20 收盘) | 快照 series_store.EURUSD 截至 2026-05-23 的最后观测日 | "2026-05-22" | "2026-05-22" | 是 |
| P009 | ①研究截止日 | M1.step3 | 并列问句窗六个月(2026-05-22 收盘→2026-11-20 收盘) | 快照 series_store.USDJPY 截至 2026-05-23 的最后观测日 | "2026-05-22" | "2026-05-22" | 是 |
| P010 | ②点值锚格 | reader_map.regions.anchor_echo[0:ECB_MRO/6个月前] | (结构化字段) | 快照 series_store.ECB_MRO 截至 2026-05-23 的最新观测值 | 2.15 | 2.15 | 是 |
| P011 | ②点值锚格 | reader_map.regions.anchor_echo[0:ECB_MRO/6个月前] | (结构化字段) | 快照 series_store.ECB_MRO 截至 2026-05-23 的最新观测月 | "2025-06" | "2025-06" | 是 |
| P012 | ②点值锚格 | reader_map.regions.anchor_echo[0:ECB_MRO/6个月前] | (结构化字段) | report.json point_values.cells[ECB_MRO].anchors[6个月前].value/observation_date(引擎面对账) | [2.15, "2025-06-11"] | [2.15, "2025-06-11"] | 是 |
| P013 | ②点值锚格 | reader_map.regions.anchor_echo[1:ECB_MRO/最新一期] | (结构化字段) | 快照 series_store.ECB_MRO 截至 2026-11-23 的最新观测值 | 2.65 | 2.65 | 是 |
| P014 | ②点值锚格 | reader_map.regions.anchor_echo[1:ECB_MRO/最新一期] | (结构化字段) | 快照 series_store.ECB_MRO 截至 2026-11-23 的最新观测月 | "2026-09" | "2026-09" | 是 |
| P015 | ②点值锚格 | reader_map.regions.anchor_echo[1:ECB_MRO/最新一期] | (结构化字段) | report.json point_values.cells[ECB_MRO].anchors[最新一期].value/observation_date(引擎面对账) | [2.65, "2026-09-16"] | [2.65, "2026-09-16"] | 是 |
| P016 | ②点值锚格 | reader_map.regions.anchor_echo[2:ECB_DFR/6个月前] | (结构化字段) | 快照 series_store.ECB_DFR 截至 2026-05-23 的最新观测值 | 2.0 | 2.0 | 是 |
| P017 | ②点值锚格 | reader_map.regions.anchor_echo[2:ECB_DFR/6个月前] | (结构化字段) | 快照 series_store.ECB_DFR 截至 2026-05-23 的最新观测月 | "2025-06" | "2025-06" | 是 |
| P018 | ②点值锚格 | reader_map.regions.anchor_echo[2:ECB_DFR/6个月前] | (结构化字段) | report.json point_values.cells[ECB_DFR].anchors[6个月前].value/observation_date(引擎面对账) | [2.0, "2025-06-11"] | [2.0, "2025-06-11"] | 是 |
| P019 | ②点值锚格 | reader_map.regions.anchor_echo[3:ECB_DFR/最新一期] | (结构化字段) | 快照 series_store.ECB_DFR 截至 2026-11-23 的最新观测值 | 2.5 | 2.5 | 是 |
| P020 | ②点值锚格 | reader_map.regions.anchor_echo[3:ECB_DFR/最新一期] | (结构化字段) | 快照 series_store.ECB_DFR 截至 2026-11-23 的最新观测月 | "2026-09" | "2026-09" | 是 |
| P021 | ②点值锚格 | reader_map.regions.anchor_echo[3:ECB_DFR/最新一期] | (结构化字段) | report.json point_values.cells[ECB_DFR].anchors[最新一期].value/observation_date(引擎面对账) | [2.5, "2026-09-16"] | [2.5, "2026-09-16"] | 是 |
| P022 | ②点值锚格 | reader_map.regions.anchor_echo[4:EA_HICP_YOY/6个月前] | (结构化字段) | 快照 series_store.EA_HICP_YOY 截至 2026-05-23 的最新观测值 | 3.0 | 3.0 | 是 |
| P023 | ②点值锚格 | reader_map.regions.anchor_echo[4:EA_HICP_YOY/6个月前] | (结构化字段) | 快照 series_store.EA_HICP_YOY 截至 2026-05-23 的最新观测月 | "2026-04" | "2026-04" | 是 |
| P024 | ②点值锚格 | reader_map.regions.anchor_echo[4:EA_HICP_YOY/6个月前] | (结构化字段) | report.json point_values.cells[EA_HICP_YOY].anchors[6个月前].value/observation_date(引擎面对账) | [3.0, "2026-04-01"] | [3.0, "2026-04-01"] | 是 |
| P025 | ②点值锚格 | reader_map.regions.anchor_echo[4:EA_HICP_YOY/6个月前] | (结构化字段) | 独立推算: 观测月末 2026-04-30 加减 +16 天(规则文本=引擎 publication_rule) | "2026-05-16" | "2026-05-16" | 是 |
| P026 | ②点值锚格 | reader_map.regions.anchor_echo[5:EA_HICP_YOY/最新一期] | (结构化字段) | 快照 series_store.EA_HICP_YOY 截至 2026-11-23 的最新观测值 | 4.0 | 4.0 | 是 |
| P027 | ②点值锚格 | reader_map.regions.anchor_echo[5:EA_HICP_YOY/最新一期] | (结构化字段) | 快照 series_store.EA_HICP_YOY 截至 2026-11-23 的最新观测月 | "2026-10" | "2026-10" | 是 |
| P028 | ②点值锚格 | reader_map.regions.anchor_echo[5:EA_HICP_YOY/最新一期] | (结构化字段) | report.json point_values.cells[EA_HICP_YOY].anchors[最新一期].value/observation_date(引擎面对账) | [4.0, "2026-10-01"] | [4.0, "2026-10-01"] | 是 |
| P029 | ②点值锚格 | reader_map.regions.anchor_echo[5:EA_HICP_YOY/最新一期] | (结构化字段) | 独立推算: 观测月末 2026-10-31 加减 +16 天(规则文本=引擎 publication_rule) | "2026-11-16" | "2026-11-16" | 是 |
| P030 | ②点值锚格 | reader_map.regions.anchor_echo[6:JP_POLICY_RATE/6个月前] | (结构化字段) | 快照 series_store.JP_POLICY_RATE 截至 2026-05-23 的最新观测值 | 0.727 | 0.727 | 是 |
| P031 | ②点值锚格 | reader_map.regions.anchor_echo[6:JP_POLICY_RATE/6个月前] | (结构化字段) | 快照 series_store.JP_POLICY_RATE 截至 2026-05-23 的最新观测月 | "2026-04" | "2026-04" | 是 |
| P032 | ②点值锚格 | reader_map.regions.anchor_echo[6:JP_POLICY_RATE/6个月前] | (结构化字段) | report.json point_values.cells[JP_POLICY_RATE].anchors[6个月前].value/observation_date(引擎面对账) | [0.727, "2026-04-01"] | [0.727, "2026-04-01"] | 是 |
| P033 | ②点值锚格 | reader_map.regions.anchor_echo[6:JP_POLICY_RATE/6个月前] | (结构化字段) | 独立推算: 观测月末 2026-04-30 加减 +5 天(规则文本=引擎 publication_rule) | "2026-05-05" | "2026-05-05" | 是 |
| P034 | ②点值锚格 | reader_map.regions.anchor_echo[7:JP_POLICY_RATE/最新一期] | (结构化字段) | 快照 series_store.JP_POLICY_RATE 截至 2026-11-23 的最新观测值 | 1.227 | 1.227 | 是 |
| P035 | ②点值锚格 | reader_map.regions.anchor_echo[7:JP_POLICY_RATE/最新一期] | (结构化字段) | 快照 series_store.JP_POLICY_RATE 截至 2026-11-23 的最新观测月 | "2026-10" | "2026-10" | 是 |
| P036 | ②点值锚格 | reader_map.regions.anchor_echo[7:JP_POLICY_RATE/最新一期] | (结构化字段) | report.json point_values.cells[JP_POLICY_RATE].anchors[最新一期].value/observation_date(引擎面对账) | [1.227, "2026-10-01"] | [1.227, "2026-10-01"] | 是 |
| P037 | ②点值锚格 | reader_map.regions.anchor_echo[7:JP_POLICY_RATE/最新一期] | (结构化字段) | 独立推算: 观测月末 2026-10-31 加减 +5 天(规则文本=引擎 publication_rule) | "2026-11-05" | "2026-11-05" | 是 |
| P038 | ②点值锚格 | reader_map.regions.anchor_echo[8:JP_CPI_YOY/6个月前] | (结构化字段) | 快照 series_store.JP_CPI_YOY 截至 2026-05-23 的最新观测值 | 1.38 | 1.38 | 是 |
| P039 | ②点值锚格 | reader_map.regions.anchor_echo[8:JP_CPI_YOY/6个月前] | (结构化字段) | 快照 series_store.JP_CPI_YOY 截至 2026-05-23 的最新观测月 | "2026-04" | "2026-04" | 是 |
| P040 | ②点值锚格 | reader_map.regions.anchor_echo[8:JP_CPI_YOY/6个月前] | (结构化字段) | report.json point_values.cells[JP_CPI_YOY].anchors[6个月前].value/observation_date(引擎面对账) | [1.38, "2026-04-01"] | [1.38, "2026-04-01"] | 是 |
| P041 | ②点值锚格 | reader_map.regions.anchor_echo[8:JP_CPI_YOY/6个月前] | (结构化字段) | 独立推算: 观测月末 2026-04-30 加减 +20 天(规则文本=引擎 publication_rule) | "2026-05-20" | "2026-05-20" | 是 |
| P042 | ②点值锚格 | reader_map.regions.anchor_echo[9:JP_CPI_YOY/最新一期] | (结构化字段) | 快照 series_store.JP_CPI_YOY 截至 2026-11-23 的最新观测值 | 2.44 | 2.44 | 是 |
| P043 | ②点值锚格 | reader_map.regions.anchor_echo[9:JP_CPI_YOY/最新一期] | (结构化字段) | 快照 series_store.JP_CPI_YOY 截至 2026-11-23 的最新观测月 | "2026-10" | "2026-10" | 是 |
| P044 | ②点值锚格 | reader_map.regions.anchor_echo[9:JP_CPI_YOY/最新一期] | (结构化字段) | report.json point_values.cells[JP_CPI_YOY].anchors[最新一期].value/observation_date(引擎面对账) | [2.44, "2026-10-01"] | [2.44, "2026-10-01"] | 是 |
| P045 | ②点值锚格 | reader_map.regions.anchor_echo[9:JP_CPI_YOY/最新一期] | (结构化字段) | 独立推算: 观测月末 2026-10-31 加减 +20 天(规则文本=引擎 publication_rule) | "2026-11-20" | "2026-11-20" | 是 |
| P046 | ②点值锚格 | reader_map.regions.anchor_echo[10:JP_CPI_TOKYO_YOY/6个月前] | (结构化字段) | 快照 series_store.JP_CPI_TOKYO_YOY 截至 2026-05-23 的最新观测值 | 1.42 | 1.42 | 是 |
| P047 | ②点值锚格 | reader_map.regions.anchor_echo[10:JP_CPI_TOKYO_YOY/6个月前] | (结构化字段) | 快照 series_store.JP_CPI_TOKYO_YOY 截至 2026-05-23 的最新观测月 | "2026-04" | "2026-04" | 是 |
| P048 | ②点值锚格 | reader_map.regions.anchor_echo[10:JP_CPI_TOKYO_YOY/6个月前] | (结构化字段) | report.json point_values.cells[JP_CPI_TOKYO_YOY].anchors[6个月前].value/observation_date(引擎面对账) | [1.42, "2026-04-01"] | [1.42, "2026-04-01"] | 是 |
| P049 | ②点值锚格 | reader_map.regions.anchor_echo[10:JP_CPI_TOKYO_YOY/6个月前] | (结构化字段) | 独立推算: 观测月末 2026-04-30 加减 −1 天(规则文本=引擎 publication_rule) | "2026-04-29" | "2026-04-29" | 是 |
| P050 | ②点值锚格 | reader_map.regions.anchor_echo[11:JP_CPI_TOKYO_YOY/最新一期] | (结构化字段) | 快照 series_store.JP_CPI_TOKYO_YOY 截至 2026-11-23 的最新观测值 | 2.73 | 2.73 | 是 |
| P051 | ②点值锚格 | reader_map.regions.anchor_echo[11:JP_CPI_TOKYO_YOY/最新一期] | (结构化字段) | 快照 series_store.JP_CPI_TOKYO_YOY 截至 2026-11-23 的最新观测月 | "2026-10" | "2026-10" | 是 |
| P052 | ②点值锚格 | reader_map.regions.anchor_echo[11:JP_CPI_TOKYO_YOY/最新一期] | (结构化字段) | report.json point_values.cells[JP_CPI_TOKYO_YOY].anchors[最新一期].value/observation_date(引擎面对账) | [2.73, "2026-10-01"] | [2.73, "2026-10-01"] | 是 |
| P053 | ②点值锚格 | reader_map.regions.anchor_echo[11:JP_CPI_TOKYO_YOY/最新一期] | (结构化字段) | 独立推算: 观测月末 2026-10-31 加减 −1 天(规则文本=引擎 publication_rule) | "2026-10-30" | "2026-10-30" | 是 |
| P054 | ③同比 | C1 | 日本全国CPI同比最新读数百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录) | 快照 series_store.JP_CPI_YOY@2026-10-01 | 2.44 | 2.44 | 是 |
| P055 | ③同比 | C1 | 日本全国CPI同比最新读数百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录) | 独立推算 2026-10-31+20天; release_calendar.entries 中 metric_id=JP_CPI_YOY 条目数 | ["2026-11-20", 0] | ["2026-11-20", 0] | 是 |
| P056 | ③同比 | C1 | 去年同月(2025-10)为百分之二点九九 | 快照 series_store.JP_CPI_YOY@2025-10-01 | 2.99 | 2.99 | 是 |
| P057 | ③同比 | C1 | 回落约零点五五个百分点 | JP_CPI_YOY@2026-10 减 @2025-10 | -0.55 | -0.55 | 是 |
| P058 | ③同比 | C1 | 近十二个月中其余十一个月里有十个月读数低于最新值 | JP_CPI_YOY 2025-11..2026-09 共 11 个月中低于 2.44 的个数 | 10 | 10 | 是 |
| P059 | ③同比 | C1 | 较一、三、六个月前分别高零点二八、零点四七、一点零六 | JP_CPI_YOY 2026-10 减 2026-09/2026-07/2026-04 | [0.28, 0.47, 1.06] | [0.28, 0.47, 1.06] | 是 |
| P060 | ③同比 | C1 | 欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16 | 快照 series_store.EA_HICP_YOY@2026-10-01 | 4.0 | 4.0 | 是 |
| P061 | ③同比 | C1 | 欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16 | 独立推算 2026-10-31+16天; 日历中覆盖 2026-10 观测月的 EA_HICP_YOY 条目数 | ["2026-11-16", 0] | ["2026-11-16", 0] | 是 |
| P062 | ③同比 | C1 | 两档形态(次月首日快报+月中终值) | release_calendar.entries RC-EA-HICP-*: first_publish_on_or_after / final_publish_on | [true, true] | [true, true] | 是 |
| P063 | ③同比 | C1 | 该读数的首发不在该终值日 | 按日历两档形态推及 2026-10 观测月: 快报日(次月首日)是否不等于引擎终值日 | true | true | 是 |
| P064 | ③同比 | C1 | 去年同月(2025-10)为百分之二点一 | 快照 series_store.EA_HICP_YOY@2025-10-01 | 2.1 | 2.1 | 是 |
| P065 | ③同比 | C1 | 抬升一点九个百分点 | EA_HICP_YOY@2026-10 减 @2025-10 | 1.9 | 1.9 | 是 |
| P066 | ③同比 | C1 | 东京都CPI同比(中旬速报先行口径)最新读数百分之二点七三(观测 2026-10,发布 2026-10-30,引擎推定规则、非日历实录) | 快照 series_store.JP_CPI_TOKYO_YOY@2026-10-01 | 2.73 | 2.73 | 是 |
| P067 | ③同比 | C1 | 东京都CPI同比(中旬速报先行口径)最新读数百分之二点七三(观测 2026-10,发布 2026-10-30,引擎推定规则、非日历实录) | 独立推算 2026-10-31−1天; 日历中 JP_CPI_TOKYO_YOY 条目数 | ["2026-10-30", 0] | ["2026-10-30", 0] | 是 |
| P068 | ③同比 | C1 | 序列自 2026-01 起 | 快照 series_store.JP_CPI_TOKYO_YOY 首/末观测月与点数 | ["2026-01", "2026-10", 10] | ["2026-01", "2026-10", 10] | 是 |
| P069 | ③同比 | C1 | 去年同月基期观测不可得、同比对照不可判 | 快照 series_store.JP_CPI_TOKYO_YOY 是否含 2025-10 | false | false | 是 |
| P070 | ⑪诚实缺席 | C1 | 该序列在当日快照 Gate A 列于 noncore_missing(来源文件在场而指标缺席) | 快照 gate_a.noncore_missing 与 noncore_missing_detail[JP_CPI_TOKYO_YOY] | [true, true] | [true, true] | 是 |
| P071 | ⑪诚实缺席 | C1 | L1 无对应事实行 | report.json layers.L1_事实层.rows 中 metric_id=JP_CPI_TOKYO_YOY 的行数 | 0 | 0 | 是 |
| P072 | ③同比 | C1 | 两条全国/全区最新读数 L1 quality_status 分别为 WARN 与 WARN | report.json layers.L1_事实层.rows[JP_CPI_YOY/EA_HICP_YOY].quality_status | ["WARN", "WARN"] | ["WARN", "WARN"] | 是 |
| P073 | ④政策面 | C2 | 欧央行主要再融资利率(ECB_MRO,政策目标口径)最新生效水平为 二点六五,观测=序列变更日=生效日 2026-09-16 | 快照 series_store.ECB_MRO 截至 2026-11-23 最后观测(日,值,是否值变更日) | ["2026-09-16", 2.65, true] | ["2026-09-16", 2.65, true] | 是 |
| P074 | ④政策面 | C2 | 决议日 2026-09-10 系引擎按『生效日前上一个周四』惯例自变更日回推 | 独立推算: 2026-09-16 之前最近的周四; report.json research_plan 引擎惯例文本含『上一个周四』 | ["2026-09-10", true] | ["2026-09-10", true] | 是 |
| P075 | ④政策面 | C2 | 冻结发布日历对欧央行无实录条目 | release_calendar.entries 中含 ECB/MRO/DFR/欧央行 的条目数 | 0 | 0 | 是 |
| P076 | ④政策面 | C2 | 欧央行存款便利利率(ECB_DFR,操作下限口径)最新生效水平 2.5%,同一变更日(2026-09-16) | 快照 series_store.ECB_DFR 截至 2026-11-23 最后观测(日,值,是否值变更日) | ["2026-09-16", 2.5, true] | ["2026-09-16", 2.5, true] | 是 |
| P077 | ④政策面 | C2 | 窗内两次上调(2026-06-17 与 2026-09-16 生效,各二十五个基点 | 快照 series_store.ECB_MRO/ECB_DFR 在 (2026-05-23,2026-11-23] 的值变更点(日,变动百分点) | [["2026-06-17", "2026-09-16"], [25.0, 25.0], ["2026-06-17", "2026-09-16"], [25.0, 25.0]] | [["2026-06-17", "2026-09-16"], [25.0, 25.0], ["2026-06-17", "2026-09-16"], [25.0, 25.0]] | 是 |
| P078 | ④政策面 | C2 | 对应决议日 2026-06-11、2026-09-10 同为惯例回推【推断】 | 独立推算: 各变更日之前最近的周四 | ["2026-06-11", "2026-09-10"] | ["2026-06-11", "2026-09-10"] | 是 |
| P079 | ④政策面 | C2 | 政策目标利率(宣布值口径,发布日历最新实录·2026-11-21 更新)约一点二五,2026-09-18 决议、2026-09-24 生效 | release_calendar.updated; entries[RC-JP-BOJ-TARGET-2026-09].{target_value,decision_date,effective_on} | ["2026-11-21", 1.25, "2026-09-18", "2026-09-24"] | ["2026-11-21", 1.25, "2026-09-18", "2026-09-24"] | 是 |
| P080 | ④政策面 | C2 | 2026-10-30 会议确认维持不变(无新调整、无生效变动) | entries[RC-JP-BOJ-MAINT-2026-10].{kind,decision_date,target_value,有无 effective_on} | ["policy_maintenance", "2026-10-30", 1.25, false] | ["policy_maintenance", "2026-10-30", 1.25, false] | 是 |
| P081 | ④政策面 | C2 | 实录无前值,属【推断】 | entries[RC-JP-BOJ-TARGET-2026-09] 中前值类字段名(prev/prior/old/before) | [] | [] | 是 |
| P082 | ④政策面 | C2 | 自 2025-11 月均零点四七八升至 2026-10 月均一点二二七 | 快照 series_store.JP_POLICY_RATE@2025-11-01 与 @2026-10-01 | [0.478, 1.227] | [0.478, 1.227] | 是 |
| P083 | ④政策面 | C2 | 2026-10-30 至研究截止二十四天内 | 独立推算: 2026-11-23 − 2026-10-30 | 24 | 24 | 是 |
| P084 | ④政策面 | C2 | 最新一期报 1.227%(观测月 2026-10,推定发布日 2026-11-05,L1 quality_status=WARN) | 快照 series_store.JP_POLICY_RATE 最新观测(月,值); 独立推算 2026-10-31+5天; L1 quality_status | ["2026-10", 1.227, "2026-11-05", "WARN"] | ["2026-10", 1.227, "2026-11-05", "WARN"] | 是 |
| P085 | ④政策面 | C2 | 六个月前锚前值为零点七二七 | 快照 series_store.JP_POLICY_RATE@2026-04-01 | 0.727 | 0.727 | 是 |
| P086 | ④政策面 | C2 | 月均口径非宣布值 | metric_registry metrics[JP_POLICY_RATE].release_semantics 含『月均 operative 利率而非决议值』 | true | true | 是 |
| P087 | ④政策面 | C2 | 惟欧央行序列止于 2026-09-16(距截止六十八天) | 快照 series_store.ECB_MRO/ECB_DFR 末观测日; 独立推算距截止天数 | ["2026-09-16", "2026-09-16", 68] | ["2026-09-16", "2026-09-16", 68] | 是 |
| P088 | ④政策面 | C2 | 无任何已决议而尚未生效的调整 | release_calendar.entries: decision_date≤2026-11-23 且 effective_on>2026-11-23 的条目; ECB 两序列窗内变更点数 | [[], 2, 2] | [[], 2, 2] | 是 |
| P089 | ④政策面 | C2 | 可核行动均已生效、无未生效决议 | release_calendar JP_POLICY_TARGET 条目: 2026-05-23 之后决议者的 effective_on 是否均 ≤ 截止日 | [["RC-JP-BOJ-TARGET-2026-09", true]] | [["RC-JP-BOJ-TARGET-2026-09", true]] | 是 |
| P090 | ④政策面 | C2 | USDJPY 水平为 159.35、SPX 水平为 7203.85、VIX 水平为 27.01 | 快照 series_store.USDJPY/SPX/VIX@2026-11-23 | [159.347, 7203.850098, 27.01] | [159.35, 7203.85, 27.01] | 是 |
| P091 | ④政策面 | C3 | 超过注册表新鲜度阈十天 | metric_registry metrics[ECB_MRO/ECB_DFR].freshness.max_calendar_lag_days | [10, 10] | [10, 10] | 是 |
| P092 | ④政策面 | C3 | 当日快照 Gate A 两序列列于 degraded 名单 | 快照 gate_a.noncore_degraded | [true, true] | [true, true] | 是 |
| P093 | ④政策面 | C3 | L1 事实行 quality_status=DEGRADED | report.json layers.L1_事实层.rows[ECB_MRO/ECB_DFR].quality_status | ["DEGRADED", "DEGRADED"] | ["DEGRADED", "DEGRADED"] | 是 |
| P094 | ④政策面 | C3 | 注册表对两序列另注决策驱动口径(观测日=政策最后确认/变更日,无更晚已证实决议不作过期) | metric_registry metrics[ECB_MRO/ECB_DFR].freshness.decision_dated 与 decision_dated_note | [true, true, true] | [true, true, true] | 是 |
| P095 | ④政策面 | C3 | 引擎点值格据此标 ok | report.json point_values.cells[ECB_MRO/ECB_DFR].anchors.*.status | ["ok"] | ["ok"] | 是 |
| P096 | ④政策面 | C3 | 发布日历(最新版,2026-11-21 更新)对欧央行无实录条目 | release_calendar.updated; 含 ECB 的条目数 | ["2026-11-21", 0] | ["2026-11-21", 0] | 是 |
| P097 | ⑪诚实缺席 | JP | 注册表无 JP_POLICY_TARGET | metric_registry.metrics 是否含 JP_POLICY_TARGET; 快照 series_store 是否含 | [false, false] | [false, false] | 是 |
| P098 | ⑬'央行目标/通胀同比 | C2 | 约一点二五,2026-09-18 决议、2026-09-24 生效 | 现行有效性: effective_on≤截止日; 其后仅维持条目; 日历无待生效条目(待生效决定与现行有效目标分记) | [true, "2026-10-30", []] | [true, "2026-10-30", []] | 是 |
| P099 | ⑬'央行目标/通胀同比 | C2 | 欧央行主要再融资利率(ECB_MRO,政策目标口径) | 注册表 metrics[ECB_MRO].calc 口径=主要再融资操作固定利率; 序列末值 2.65 自 2026-09-16 起至截止日无更新 | [true, "2026-09-16"] | [true, "2026-09-16"] | 是 |
| P100 | ⑬'央行目标/通胀同比 | C2 | 欧央行存款便利利率(ECB_DFR,操作下限口径) | 注册表 metrics[ECB_DFR].calc 口径=存款便利利率 fixed rate(与 MRO 分列) | true | true | 是 |
| P101 | ⑤三利率分解 | reader_map.rates_decomposition | (结构化字段) | 快照 series_store.UST_10Y/TIPS_10Y/BEI_10Y @2026-10-20→@2026-11-19 之差×100 | [-8.0, 11.0, -19.0] | [-8.0, 11.0, -19.0] | 是 |
| P102 | ⑤三利率分解 | reader_map.rates_decomposition | (结构化字段) | report.json research_plan.us_rates_trio.window.from/to | ["2026-10-20", "2026-11-19"] | ["2026-10-20", "2026-11-19"] | 是 |
| P103 | ⑤三利率分解 | reader_map.rates_decomposition | (结构化字段) | 恒等式 名义=实际+盈亏平衡(直算) | -8.0 | -8.0 | 是 |
| P104 | ⑤三利率分解 | reader_map.rates_decomposition | (结构化字段) | report.json us_rates_trio.chg_bp(引擎面对账) | [-8.0, 11.0, -19.0] | [-8.0, 11.0, -19.0] | 是 |
| P105 | ⑤资产月窗 | reader_map.asset_returns_echo[NIKKEI225] | (结构化字段) | 快照 series_store.NIKKEI225@2026-10-23→@2026-11-20 涨幅%; 起止观测日=截至窗起/截止日最后观测 | [-9.979574, "2026-10-23", "2026-11-20"] | [-9.98, "2026-10-23", "2026-11-20"] | 是 |
| P106 | ⑤资产月窗 | reader_map.asset_returns_echo[NIKKEI225] | (结构化字段) | report.json research_plan.asset_moves.rows[NIKKEI225].chg_pct/window 与 window_months | [-9.98, "2026-10-23", "2026-11-20", 1] | [-9.98, "2026-10-23", "2026-11-20", 1] | 是 |
| P107 | ⑤资产月窗 | reader_map.asset_returns_echo[DAX] | (结构化字段) | 快照 series_store.DAX@2026-10-23→@2026-11-23 涨幅%; 起止观测日=截至窗起/截止日最后观测 | [0.110393, "2026-10-23", "2026-11-23"] | [0.11, "2026-10-23", "2026-11-23"] | 是 |
| P108 | ⑤资产月窗 | reader_map.asset_returns_echo[DAX] | (结构化字段) | report.json research_plan.asset_moves.rows[DAX].chg_pct/window 与 window_months | [0.11, "2026-10-23", "2026-11-23", 1] | [0.11, "2026-10-23", "2026-11-23", 1] | 是 |
| P109 | ⑤资产月窗 | reader_map.asset_returns_echo[SPX] | (结构化字段) | 快照 series_store.SPX@2026-10-23→@2026-11-23 涨幅%; 起止观测日=截至窗起/截止日最后观测 | [-5.506921, "2026-10-23", "2026-11-23"] | [-5.51, "2026-10-23", "2026-11-23"] | 是 |
| P110 | ⑤资产月窗 | reader_map.asset_returns_echo[SPX] | (结构化字段) | report.json research_plan.asset_moves.rows[SPX].chg_pct/window 与 window_months | [-5.51, "2026-10-23", "2026-11-23", 1] | [-5.51, "2026-10-23", "2026-11-23", 1] | 是 |
| P111 | ⑤资产月窗 | reader_map.asset_returns_echo[VIX] | (结构化字段) | 快照 series_store.VIX@2026-10-23→@2026-11-23 涨幅%; 起止观测日=截至窗起/截止日最后观测 | [38.868887, "2026-10-23", "2026-11-23"] | [38.87, "2026-10-23", "2026-11-23"] | 是 |
| P112 | ⑤资产月窗 | reader_map.asset_returns_echo[VIX] | (结构化字段) | report.json research_plan.asset_moves.rows[VIX].chg_pct/window 与 window_months | [38.87, "2026-10-23", "2026-11-23", 1] | [38.87, "2026-10-23", "2026-11-23", 1] | 是 |
| P113 | ⑥转折判断 | W1 | (结构化字段) | 快照 series_store.JP_CPI_YOY@2025-11-01 与 @2026-02-01 | [2.9, 1.27] | [2.9, 1.27] | 是 |
| P114 | ⑥转折判断 | W2 | (结构化字段) | 快照 series_store.EA_HICP_YOY@2026-02-01 与 @2026-05-01 | [1.9, 3.2] | [1.9, 3.2] | 是 |
| P115 | ⑥转折判断 | W3 | (结构化字段) | 快照 series_store.JP_POLICY_RATE@2026-04-01 与 @2026-07-01 | [0.727, 0.978] | [0.727, 0.978] | 是 |
| P116 | ⑥转折判断 | W1.first_mover | 2025-11→2026-02 由 2.9 降至 1.27(三个月 -1.63 个百分点 | 快照 series_store.JP_CPI_YOY@2025-11-01/@2026-02-01 及其差 | [2.9, 1.27, -1.63] | [2.9, 1.27, -1.63] | 是 |
| P117 | ⑥转折判断 | W1.first_mover | 候选池内最大单段变动 | report.json turning_candidates.candidates 中 /delta/ 最大者及其 metric_id/to_ym | [1.63, ["JP_CPI_YOY"], ["2026-02"]] | [1.63, ["JP_CPI_YOY"], ["2026-02"]] | 是 |
| P118 | ⑥转折判断 | W1.follow_or_diverge | 同期欧元区 HICP 亦下行(2025-11 2.1→2026-02 1.9) | 快照 series_store.EA_HICP_YOY@2025-11-01/@2026-02-01 | [2.1, 1.9] | [2.1, 1.9] | 是 |
| P119 | ⑥转折判断 | W1.follow_or_diverge | 两地谷底相邻(欧元区 2026-01 的 1.7、日本 2026-02 的 1.27) | 快照 series_store.EA_HICP_YOY / JP_CPI_YOY 在 2025-01..2026-10 的最小值(值,月) | [[1.7, "2026-01"], [1.27, "2026-02"]] | [[1.7, "2026-01"], [1.27, "2026-02"]] | 是 |
| P120 | ⑥转折判断 | W1.follow_or_diverge | 按引擎候选面转折日(区间终点月)则为日本(2026-02)先于欧元区(2026-05) | report.json turning_candidates.candidates[].to_ym(JP_CPI_YOY / EA_HICP_YOY) | [["2026-02"], ["2026-05"]] | [["2026-02"], ["2026-05"]] | 是 |
| P121 | ⑥转折判断 | W1.narrative | 2026-03 1.46、2026-04 1.38、2026-05 1.53、2026-06 1.67、2026-07 1.97、2026-08 1.98、2026-09 2.16、2026-10 2.44 | 快照 series_store.JP_CPI_YOY@2026-03..2026-10 | [1.46, 1.38, 1.53, 1.67, 1.97, 1.98, 2.16, 2.44] | [1.46, 1.38, 1.53, 1.67, 1.97, 1.98, 2.16, 2.44] | 是 |
| P122 | ⑥转折判断 | W1.narrative | 日本通胀谷底转折: 此后总体回升、非逐月单调 | 快照 series_store.JP_CPI_YOY 2026-02→2026-10 净变动>0 且存在环比下降月 | [true, true] | [true, true] | 是 |
| P123 | ⑥转折判断 | W1.narrative | 谷底月前的 BOJ 月均台阶(2026-01 0.728) | 快照 series_store.JP_POLICY_RATE@2026-01-01 | 0.728 | 0.728 | 是 |
| P124 | ⑥转折判断 | W2.first_mover | 2026-02→2026-05 由 1.9 升至 3.2(三个月 +1.30 个百分点) | 快照 series_store.EA_HICP_YOY@2026-02-01/@2026-05-01 及其差 | [1.9, 3.2, 1.3] | [1.9, 3.2, 1.3] | 是 |
| P125 | ⑥转折判断 | W2.follow_or_diverge | 日本端同窗自谷底回升(2026-02 1.27→2026-05 1.53) | 快照 series_store.JP_CPI_YOY@2026-02-01/@2026-05-01 | [1.27, 1.53] | [1.27, 1.53] | 是 |
| P126 | ⑥转折判断 | W2.follow_or_diverge | 生效日 2026-06-17 晚于转折段终点月 2026-05 | 快照 series_store.ECB_MRO 值变更日 2026-06-17 与观测月 2026-05 先后 | true | true | 是 |
| P127 | ⑥转折判断 | W2.narrative | 2026-06 2.8、2026-07 2.9、2026-08 3.2、2026-09 3.8、2026-10 4.0 | 快照 series_store.EA_HICP_YOY@2026-06..2026-10 | [2.8, 2.9, 3.2, 3.8, 4.0] | [2.8, 2.9, 3.2, 3.8, 4.0] | 是 |
| P128 | ⑥转折判断 | W3.first_mover | 2026-04 0.727→2026-07 0.978(经 2026-06 0.841 过渡) | 快照 series_store.JP_POLICY_RATE@2026-04-01/@2026-06-01/@2026-07-01 | [0.727, 0.841, 0.978] | [0.727, 0.841, 0.978] | 是 |
| P129 | ⑥转折判断 | W3.narrative | 2026-08 0.977、2026-09 1.043、2026-10 1.227 | 快照 series_store.JP_POLICY_RATE@2026-08..2026-10 | [0.977, 1.043, 1.227] | [0.977, 1.043, 1.227] | 是 |
| P130 | ⑥转折判断 | W3.narrative | 与月均台阶 2026-09→2026-10(1.043→1.227)相容 | JP_POLICY_RATE@2026-09-01/@2026-10-01; 日历生效日 2026-09-24 落在 9 月月内(月均口径滞后体现) | [1.043, 1.227, true] | [1.043, 1.227, true] | 是 |
| P131 | ⑦传导链 | M1.step1 | EA_HICP_YOY 2026-02 的 1.9 升至 2026-05 的 3.2 | 快照 series_store.EA_HICP_YOY@2026-02-01/@2026-05-01 | [1.9, 3.2] | [1.9, 3.2] | 是 |
| P132 | ⑦传导链 | M1.step1 | (2026-06 一度回落至 2.8) | 快照 series_store.EA_HICP_YOY@2026-06-01 | 2.8 | 2.8 | 是 |
| P133 | ⑦传导链 | M1.step1 | 2026-10 达 4.0 | 快照 series_store.EA_HICP_YOY@2026-10-01 | 4.0 | 4.0 | 是 |
| P134 | ⑦传导链 | M1.step1 | JP_CPI_YOY 自 2025-01 的局部高点 4.03 回落 | 快照 series_store.JP_CPI_YOY@2025-01-01 | 4.03 | 4.03 | 是 |
| P135 | ⑦传导链 | M1.step1 | 此后至最新观测月未再越过 | 快照 series_store.JP_CPI_YOY 2025-02..2026-10 最大值及其是否 <4.03 | [3.66, true] | [3.66, true] | 是 |
| P136 | ⑦传导链 | M1.step1 | 全序列最高为 2023-01 的 4.31 | 快照 series_store.JP_CPI_YOY 全序列最大值(月,值) | ["2023-01", 4.31] | ["2023-01", 4.31] | 是 |
| P137 | ⑦传导链 | M1.step1 | 2025-09、2025-10 两度小幅回升至 2.91、2.99 | 快照 series_store.JP_CPI_YOY@2025-09-01/@2025-10-01 | [2.91, 2.99] | [2.91, 2.99] | 是 |
| P138 | ⑦传导链 | M1.step1 | 非逐月单调 | 快照 series_store.JP_CPI_YOY 2025-01..2026-02 环比上升的月份 | ["2025-09", "2025-10"] | ["2025-09", "2025-10"] | 是 |
| P139 | ⑦传导链 | M1.step1 | 经 2025-07 的 3.1 至 2026-02 的 1.27 | 快照 series_store.JP_CPI_YOY@2025-07-01/@2026-02-01 | [3.1, 1.27] | [3.1, 1.27] | 是 |
| P140 | ⑦传导链 | M1.step1 | 此后总体回升至 2026-10 的 2.44 | 快照 series_store.JP_CPI_YOY@2026-10-01(及是否高于 2026-02) | [2.44, true] | [2.44, true] | 是 |
| P141 | ⑦传导链 | M1.step1 | JP_CPI_YOY 为注册表 2025基/2020基 拼接 同月同比(新基优先,重叠差>0.10pp 告警) | metric_registry metrics[JP_CPI_YOY].calc | [true, true, true] | [true, true, true] | 是 |
| P142 | ⑦传导链 | M1.step2 | ECB 两次变更各 25bp: 2026-06-17 生效,MRO 2.15→2.4、DFR 2.0→2.25 | 快照 series_store.ECB_MRO/ECB_DFR 2026-06-17 变更前→变更后 | [2.15, 2.4, 2.0, 2.25] | [2.15, 2.4, 2.0, 2.25] | 是 |
| P143 | ⑦传导链 | M1.step2 | 2026-09-16 生效,MRO 2.4→2.65、DFR 2.25→2.5 | 快照 series_store.ECB_MRO/ECB_DFR 2026-09-16 变更前→变更后 | [2.4, 2.65, 2.25, 2.5] | [2.4, 2.65, 2.25, 2.5] | 是 |
| P144 | ⑦传导链 | M1.step2 | 冻结发布日历无 ECB 实录,发布面=序列变更日 | release_calendar 含 ECB 条目数; 两序列末观测日=末变更日 | [0, true, true] | [0, true, true] | 是 |
| P145 | ⑦传导链 | M1.step2 | BOJ 2026-09-18 决议(2026-09-24 生效)目标约 1.25%(发布日历实录) | release_calendar entries[RC-JP-BOJ-TARGET-2026-09].decision_date/effective_on/target_value | ["2026-09-18", "2026-09-24", 1.25] | ["2026-09-18", "2026-09-24", 1.25] | 是 |
| P146 | ⑦传导链 | M1.step2 | 2026-10-30 会议确认维持 | release_calendar entries[RC-JP-BOJ-MAINT-2026-10].decision_date | ["2026-10-30"] | ["2026-10-30"] | 是 |
| P147 | ⑦传导链 | M1.step2 | JP_POLICY_RATE 2026-09→2026-10 的台阶(1.043→1.227) | 快照 series_store.JP_POLICY_RATE@2026-09-01/@2026-10-01 | [1.043, 1.227] | [1.043, 1.227] | 是 |
| P148 | ⑦传导链 | M1.step2 | 其余月均台阶在发布日历无对应实录 | 近 12 个月 JP_POLICY_RATE 月均变动点数(整数 bp 非零;严格不等比较另含两次 -0.1bp 舍入伪变动) vs 日历中改变目标的 JP 条目数 | [6, 1] | [6, 1] | 是 |
| P149 | ⑦传导链 | M1.step3 | MRO 2.65% vs BOJ 目标约 1.25% | 快照 series_store.ECB_MRO@2026-09-16; 日历 target_value | [2.65, 1.25] | [2.65, 1.25] | 是 |
| P150 | ⑦传导链 | M1.step3 | 联邦基金目标区间 3.75%–4.00%,DFEDTARL/DFEDTARU 2026-11-23 观测 | 快照 series_store.DFEDTARL/DFEDTARU 截至 2026-11-23 最后观测(日,值) | [["2026-11-23", 3.75], ["2026-11-23", 4.0]] | [["2026-11-23", 3.75], ["2026-11-23", 4.0]] | 是 |
| P151 | ⑦传导链 | M1.step3 | 不在本轮证据索引 | report.json evidence_index 中 DFEDTARL/DFEDTARU 行数 | 0 | 0 | 是 |
| P152 | ⑦传导链 | M1.step3 | UST_10Y 最新 5.04% | 快照 series_store.UST_10Y 截至 2026-11-23 最后观测(值;观测日见注) | 5.04 | 5.04 | 是 |
| P153 | ⑦传导链 | M1.step3 | 2026-10-23 收盘 175.61→2026-11-20 收盘 175.19(-0.24%) | 快照 series_store.EURUSD×USDJPY 同日相乘 @2026-10-23/@2026-11-20 及涨跌幅% | [175.609119, 175.194108, -0.236327] | [175.61, 175.19, -0.24] | 是 |
| P154 | ⑦传导链 | M1.step3 | 至 2026-11-23 盘中 174.32(较 10-23 -0.73%) | 快照 series_store.EURUSD×USDJPY @2026-11-23 及较 10-23 涨跌幅% | [174.321156, -0.733426] | [174.32, -0.73] | 是 |
| P155 | ⑦传导链 | M1.step3 | 合成交叉盘由 184.80 降至 175.19(-5.20%;腿: EURUSD -5.61%、USDJPY +0.43%) | 快照 series_store.EURUSD/USDJPY@2026-05-22→@2026-11-20(合成交叉盘起止与涨跌幅%,两腿涨跌幅%) | [184.797209, 175.194108, -5.196561, -5.605555, 0.433282] | [184.8, 175.19, -5.2, -5.61, 0.43] | 是 |
| P156 | ⑦传导链 | M1.step3 | 减日本政策利率 2026-05 月均 0.727% 得 1.423 个百分点 | MRO 2.15(2026-06-17 变更前) − JP_POLICY_RATE@2026-05 | [0.727, 1.423] | [0.727, 1.423] | 是 |
| P157 | ⑦传导链 | M1.step3 | 减 2026-10 月均 1.227% 得 1.423 个百分点 | MRO 2.65 − JP_POLICY_RATE@2026-10 | 1.423 | 1.423 | 是 |
| P158 | ⑦传导链 | M1.step3 | 欧央行两度上调合计 0.5 个百分点、日本政策利率月均亦抬升 0.5 个百分点 | MRO 窗内变更点变动之和; JP_POLICY_RATE@2026-10 − @2026-04 | [0.5, 0.5] | [0.5, 0.5] | 是 |
| P159 | ⑦传导链 | M1.step3 | EURUSD 由 1.1221 降至 1.0970(-2.24%)、USDJPY 由 156.494 升至 159.707(+2.05%)、DXY 由 101.81 升至 103.81(+1.96%) | 快照 series_store.EURUSD/USDJPY/DXY@2026-10-23→@2026-11-20(起,止,涨跌幅%) | [1.122146, 1.096972, -2.24338, 156.494003, 159.707001, 2.053113, 101.809998, 103.809998, 1.964444] | [1.1221, 1.097, -2.24, 156.494, 159.707, 2.05, 101.81, 103.81, 1.96] | 是 |
| P160 | ⑦传导链 | M1.step3 | EURUSD 1.0940(-2.51%)、USDJPY 159.347(+1.82%)、DXY 104.079(+2.23%) | 快照 series_store.EURUSD/USDJPY/DXY@2026-10-23→@2026-11-23(起,止,涨跌幅%) | [1.122146, 1.093972, -2.510725, 156.494003, 159.347, 1.823071, 101.809998, 104.079002, 2.228665] | [1.1221, 1.094, -2.51, 156.494, 159.347, 1.82, 101.81, 104.079, 2.23] | 是 |
| P161 | ⑦传导链 | M1.step4 | SPX 下跌 9.36%、NIKKEI225 下跌 9.98%、DAX 下跌 1.50%、CAC40 上涨 1.86% | 快照 series_store.SPX/NIKKEI225/DAX/CAC40@2026-10-23→@2026-11-20 涨跌幅% | [-9.356243, -9.979574, -1.504552, 1.862181] | [-9.36, -9.98, -1.5, 1.86] | 是 |
| P162 | ⑦传导链 | M1.step4 | VIX 由 19.45 升至 35.89(+84.5%) | 快照 series_store.VIX@2026-10-23/@2026-11-20 | [19.450001, 35.889999, 84.524407] | [19.45, 35.89, 84.5] | 是 |
| P163 | ⑦传导链 | M1.step4 | 11-13 19.30→11-16 22.91→11-17 25.46→11-18 24.56→11-19 28.44→11-20 35.89 | 快照 series_store.VIX@2026-11-13..2026-11-20 | [19.299999, 22.91, 25.459999, 24.559999, 28.440001, 35.889999] | [19.3, 22.91, 25.46, 24.56, 28.44, 35.89] | 是 |
| P164 | ⑦传导链 | M1.step4 | 末六个交易日收盘路径 | 快照 series_store.VIX 截至 2026-11-20 的最后 6 个观测日 | ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"] | ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"] | 是 |
| P165 | ⑦传导链 | M1.step4 | SPX -5.51%(7203.85,盘中)、DAX +0.11%(25209.45,盘中)、NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)、VIX +38.87%(27.01,盘中 | 快照 series_store.SPX/DAX/NIKKEI225/VIX@2026-10-23→截至截止日最后观测(涨跌幅%,末值,观测日) | [-5.506921, 7203.85, "2026-11-23", 0.110393, 25209.45, "2026-11-23", -9.979574, 56436.65, "2026-11-20", 38.868887, 27.01, "2026-11-23"] | [-5.51, 7203.85, "2026-11-23", 0.11, 25209.45, "2026-11-23", -9.98, 56436.65, "2026-11-20", 38.87, 27.01, "2026-11-23"] | 是 |
| P166 | ⑦传导链 | M1.step4 | 较 2026-11-20 收盘 -24.7% | 快照 series_store.VIX@2026-11-23 对 @2026-11-20 涨跌幅% | -24.742266 | -24.7 | 是 |
| P167 | ⑦传导链 | M1.step4 | 2026-11-04→11-05 VIX 收盘 16.61→28.18(+69.66%) | 快照 series_store.VIX@2026-11-04/@2026-11-05 | [16.610001, 28.18, 69.656823] | [16.61, 28.18, 69.66] | 是 |
| P168 | ⑦传导链 | M1.step4 | 至 11-11 回落至 17.49(四个交易日,较 11-05 -37.93%) | 快照 series_store.VIX@2026-11-11; 2026-11-05 之后至 11-11 观测数; 较 11-05 涨跌幅% | [17.49, 4, -37.934705] | [17.49, 4, -37.93] | 是 |
| P169 | ⑦传导链 | M1.step4 | 同期 SPX 11-05 -4.36%,下一交易日 NIKKEI225 11-06 -5.96% | 快照 series_store.SPX@2026-11-04→11-05; NIKKEI225@2026-11-05→11-06 | [-4.35566, -5.964727] | [-4.36, -5.96] | 是 |
| P170 | ⑦传导链 | M1.step4 | 当日 VIX +18.70%/+26.20%,为窗内两个最大单日跳升日 | 快照 series_store.VIX 2026-11-16/11-20 单日涨跌幅%; 窗内单日涨幅前二 | [18.704669, 26.195491, ["2026-11-20", "2026-11-16"]] | [18.7, 26.2, ["2026-11-20", "2026-11-16"]] | 是 |
| P171 | ⑦传导链 | M1.step4 | 2026-11-13→2026-11-20: SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27% | 快照 series_store.四股指@2026-11-13→@2026-11-20 涨跌幅% | [-8.612909, -7.696302, -7.279154, -5.271417] | [-8.61, -7.7, -7.28, -5.27] | 是 |
| P172 | ⑦传导链 | M1.step4 | 两日欧元、日元对美元单日变动幅度不超过 0.23% | 快照 series_store.EURUSD/USDJPY 2026-11-16 与 11-20 单日涨跌幅%的最大绝对值≤0.235 | true | true | 是 |
| P173 | ⑦传导链 | M1.step4 | 单日看 2026-11-20 NIKKEI225 -5.06% 深于 SPX -3.70% | 快照 series_store.NIKKEI225/SPX@2026-11-20 单日涨跌幅% | [-5.059467, -3.699083] | [-5.06, -3.7] | 是 |
| P174 | ⑦传导链 | M1.step4 | 为窗内四地最大单日跌幅 | 快照 series_store.四股指 11-13..11-20 单日涨跌幅最小值(指标,日) | ["NIKKEI225", "2026-11-20"] | ["NIKKEI225", "2026-11-20"] | 是 |
| P175 | ⑦传导链 | M1.step4 | FOMC 2026年10月会议纪要 2026-11-18 发布 | report.json research_plan.policy_doc_facts[0].{title,published_on} | ["FOMC 2026年10月会议纪要", "2026-11-18"] | ["FOMC 2026年10月会议纪要", "2026-11-18"] | 是 |
| P176 | ⑦传导链(reader_map) | HC | 日本全国 CPI 同比最新读数 2.44%(观测 2026-10,发布 2026-11-20,推定规则) | 快照 series_store.JP_CPI_YOY@2026-10-01 | 2.44 | 2.44 | 是 |
| P177 | ⑦传导链(reader_map) | HC | 低于去年同月(2025-10 为 2.99) | 快照 series_store.JP_CPI_YOY@2025-10-01 | 2.99 | 2.99 | 是 |
| P178 | ⑦传导链(reader_map) | HC | 欧元区 HICP 同比 4.0%(观测 2026-10,推定终值发布日 2026-11-16,推定规则) | 快照 series_store.EA_HICP_YOY@2026-10-01 | 4.0 | 4.0 | 是 |
| P179 | ⑦传导链(reader_map) | HC | 高于去年同月(2025-10 为 2.1) | 快照 series_store.EA_HICP_YOY@2025-10-01 | 2.1 | 2.1 | 是 |
| P180 | ⑦传导链(reader_map) | HC | 较六个月前锚两地读数均上行 | 快照 series_store.JP_CPI_YOY/EA_HICP_YOY 2026-10 减 2026-04 是否 >0 | [true, true] | [true, true] | 是 |
| P181 | ⑦传导链(reader_map) | HC | 依据月均市场利率台阶 0.478→1.227 | 快照 series_store.JP_POLICY_RATE@2025-11-01/@2026-10-01 | [0.478, 1.227] | [0.478, 1.227] | 是 |
| P182 | ⑦传导链(reader_map) | HC | 日本央行政策目标约 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持 | release_calendar: target_value/decision_date/effective_on/维持条目 decision_date | [1.25, "2026-09-18", "2026-09-24", "2026-10-30"] | [1.25, "2026-09-18", "2026-09-24", "2026-10-30"] | 是 |
| P183 | ⑦传导链(reader_map) | HC | 欧央行主要再融资利率 2.65%/存款便利利率 2.5%(2026-09-16 生效;决议日 2026-09-10 | 快照 series_store.ECB_MRO/ECB_DFR@2026-09-16; 独立推算其前最近周四 | [2.65, 2.5, "2026-09-10"] | [2.65, 2.5, "2026-09-10"] | 是 |
| P184 | ⑦传导链(reader_map) | HC | 最近六个月两次同幅上调 | 快照 series_store.ECB_MRO 窗内变更点(日,变动bp) | [["2026-06-17", "2026-09-16"], [25.0, 25.0]] | [["2026-06-17", "2026-09-16"], [25.0, 25.0]] | 是 |
| P185 | ⑦传导链(reader_map) | HC | 惟欧央行序列止于 2026-09-16(距截止 68 天,Gate A 列 degraded) | 快照 series_store.ECB_MRO 末观测日; 距截止天数; gate_a.noncore_degraded | ["2026-09-16", 68, true] | ["2026-09-16", 68, true] | 是 |
| P186 | ⑦传导链(reader_map) | EA | 欧央行主要再融资利率(政策目标口径)由6个月前锚(观测 2025-06-11)的 2.15% 升至最新一期锚(观测 2026-09-16)的 2.65% | 快照 series_store.ECB_MRO 截至 2026-05-23 / 2026-11-23 的最后观测(日,值) | [["2025-06-11", 2.15], ["2026-09-16", 2.65]] | [["2025-06-11", 2.15], ["2026-09-16", 2.65]] | 是 |
| P187 | ⑦传导链(reader_map) | EA | 由 2.0% 升至 2.5% | 快照 series_store.ECB_DFR 截至 2026-05-23 / 2026-11-23 的最后观测值 | [2.0, 2.5] | [2.0, 2.5] | 是 |
| P188 | ⑦传导链(reader_map) | EA | 两次变更(2026-06-17 生效、2026-09-16 生效,各 +25bp | 快照 series_store.ECB_DFR 窗内变更点(日,变动bp) | [["2026-06-17", "2026-09-16"], [25.0, 25.0]] | [["2026-06-17", "2026-09-16"], [25.0, 25.0]] | 是 |
| P189 | ⑦传导链(reader_map) | EA | HICP 同比由6个月前锚(观测月 2026-04)的 3.0% 至最新一期锚(观测月 2026-10)的 4.0% | 快照 series_store.EA_HICP_YOY@2026-04-01/@2026-10-01 | [3.0, 4.0] | [3.0, 4.0] | 是 |
| P190 | ⑦传导链(reader_map) | EA | 相比去年同月(2025-10 为 2.1)高 1.9 个百分点 | EA_HICP_YOY@2026-10 减 @2025-10 | [2.1, 1.9] | [2.1, 1.9] | 是 |
| P191 | ⑦传导链(reader_map) | EA | 路径: 2026-01 谷底 1.7→2026-02 1.9→2026-05 3.2→2026-06 2.8→2026-10 4.0 | 快照 series_store.EA_HICP_YOY@2026-01/02/05/06/10 | [1.7, 1.9, 3.2, 2.8, 4.0] | [1.7, 1.9, 3.2, 2.8, 4.0] | 是 |
| P192 | ⑦传导链(reader_map) | EA | 最新读数为近十二个月最高 | 快照 series_store.EA_HICP_YOY 2025-11..2026-10 最大值及是否等于 2026-10 值 | [4.0, true] | [4.0, true] | 是 |
| P193 | ⑦传导链(reader_map) | EA | 发布 2026-11-16 为引擎推定规则下的终值日 | 独立推算 2026-10-31+16天 | "2026-11-16" | "2026-11-16" | 是 |
| P194 | ⑦传导链(reader_map) | JP | 发布日历实录(v1.5.0,2026-11-21 更新)政策目标利率约 1.25% | release_calendar.version/updated; target_value | ["1.5.0", "2026-11-21", 1.25] | ["1.5.0", "2026-11-21", 1.25] | 是 |
| P195 | ⑦传导链(reader_map) | JP | 由6个月前锚(观测月 2026-04)的 0.727% 台阶升至最新一期锚(观测月 2026-10)的 1.227% | 快照 series_store.JP_POLICY_RATE@2026-04-01/@2026-10-01 | [0.727, 1.227] | [0.727, 1.227] | 是 |
| P196 | ⑦传导链(reader_map) | JP | 近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp | 快照 series_store.JP_POLICY_RATE@2025-11-01/@2026-10-01 及差×100 | [0.478, 1.227, 75] | [0.478, 1.227, 75] | 是 |
| P197 | ⑦传导链(reader_map) | JP | 净 +75bp=六个变动点之和,窗口 2025-11-23..2026-11-23 | 快照 series_store.JP_POLICY_RATE 窗 (2025-11-23,2026-11-23] 变动点数与变动和(bp); 窗启时在值/窗末值 | [6, 75, 75.1, 0.478, 1.227] | [6, 75, 75.1, 0.478, 1.227] | 是 |
| P198 | ⑦传导链(reader_map) | JP | 引擎政策一年窗路径同口径 | report.json point_values.cells[JP_POLICY_RATE].policy_window_path.{window,net_bp,window_start_value,window_end_value} | [["2025-11-23", "2026-11-23"], 75, 0.478, 1.227] | [["2025-11-23", "2026-11-23"], 75, 0.478, 1.227] | 是 |
| P199 | ⑦传导链(reader_map) | JP | 2026-09→2026-10 台阶(1.043→1.227) | 快照 series_store.JP_POLICY_RATE@2026-09-01/@2026-10-01 | [1.043, 1.227] | [1.043, 1.227] | 是 |
| P200 | ⑦传导链(reader_map) | JP | 全国 CPI 同比由6个月前锚(观测月 2026-04)的 1.38% 升至最新一期锚(观测月 2026-10)的 2.44% | 快照 series_store.JP_CPI_YOY@2026-04-01/@2026-10-01 | [1.38, 2.44] | [1.38, 2.44] | 是 |
| P201 | ⑦传导链(reader_map) | JP | 最新读数相比去年同月(2025-10 为 2.99)低 0.55 个百分点 | JP_CPI_YOY@2025-10 与 2026-10 之差(绝对值) | [2.99, 0.55] | [2.99, 0.55] | 是 |
| P202 | ⑦传导链(reader_map) | JP | 由6个月前锚观测月 2026-04 的 1.42% 升至最新一期锚观测月 2026-10 的 2.73% | 快照 series_store.JP_CPI_TOKYO_YOY@2026-04-01/@2026-10-01 | [1.42, 2.73] | [1.42, 2.73] | 是 |
| P203 | ⑦传导链(reader_map) | TL1.observed_fact | EA_HICP_YOY 2026-02 1.9→2026-05 3.2→2026-10 4.0 | 快照 series_store.EA_HICP_YOY@2026-02/05/10 | [1.9, 3.2, 4.0] | [1.9, 3.2, 4.0] | 是 |
| P204 | ⑦传导链(reader_map) | TL1.observed_fact | JP_CPI_YOY 2026-02 1.27→2026-10 2.44 | 快照 series_store.JP_CPI_YOY@2026-02-01/@2026-10-01 | [1.27, 2.44] | [1.27, 2.44] | 是 |
| P205 | ⑦传导链(reader_map) | TL1.main_predicts | 决议日(回推 2026-06-11)前可见 2026-04=3.0、生效日前可见 2026-05=3.2 | 引擎规则(观测月末+16天)下 ≤2026-06-11 / ≤2026-06-17 已入档的最新观测月与值(读数=快照最新修订值) | ["2026-04", 3.0, "2026-05", 3.2] | ["2026-04", 3.0, "2026-05", 3.2] | 是 |
| P206 | ⑦传导链(reader_map) | TL1.main_predicts | 决议日(回推 2026-09-10)前可见 2026-07=2.9、生效日前可见 2026-08=3.2 | 引擎规则下 ≤2026-09-10 / ≤2026-09-16 已入档的最新观测月与值 | ["2026-07", 2.9, "2026-08", 3.2] | ["2026-07", 2.9, "2026-08", 3.2] | 是 |
| P207 | ⑦传导链(reader_map) | TL1.verdict_note | 发布日 2026-09-16 与生效日同日 | 独立推算 2026-08 观测月的引擎发布日(月末+16天) | "2026-09-16" | "2026-09-16" | 是 |
| P208 | ⑦传导链(reader_map) | TL1.verdict_note | 两序列自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371 天 | 快照 series_store.ECB_MRO/ECB_DFR@2025-06-11(日,值); 开区间 (2025-06-11,2026-06-17) 内变更点数; 天数差 | [["2025-06-11", 2.15], ["2025-06-11", 2.0], 0, 0, 371] | [["2025-06-11", 2.15], ["2025-06-11", 2.0], 0, 0, 371] | 是 |
| P209 | ⑦传导链(reader_map) | TL1.verdict_note | 其间读数已由 2026-01 的 1.7 升至 2026-04 的 3.0 而未触发变更 | 快照 series_store.EA_HICP_YOY@2026-01-01/@2026-04-01 | [1.7, 3.0] | [1.7, 3.0] | 是 |
| P210 | ⑦传导链(reader_map) | TL1.verdict_note | 两次变更相隔 91 天、各 25bp | 快照 series_store.ECB_MRO 两变更点间隔天数与变动bp | [91, [25.0, 25.0]] | [91, [25.0, 25.0]] | 是 |
| P211 | ⑦传导链(reader_map) | TL1.verdict_note | 第二次变更的决议日前可见读数 2.9 低于 2026-05 峰值 3.2 | 快照 series_store.EA_HICP_YOY@2026-07-01/@2026-05-01 | [2.9, 3.2, true] | [2.9, 3.2, true] | 是 |
| P212 | ⑦传导链(reader_map) | TL1.verdict_note | 两次变更决议日前可见读数为 2026-05 的 3.2 与 2026-08 的 3.2 | 按日历两档形态(次月首日快报) ≤2026-06-11 / ≤2026-09-10 已发布的最新观测月与值(读数=快照最新修订值) | ["2026-05", 3.2, "2026-08", 3.2] | ["2026-05", 3.2, "2026-08", 3.2] | 是 |
| P213 | ⑦传导链(reader_map) | TL2.observed_fact | 由 2026-10-23 的约 175.61 降至 2026-11-20 的约 175.19(-0.24%)、2026-11-23 盘中约 174.32(-0.73%) | 快照 series_store.EURUSD×USDJPY@2026-10-23/@2026-11-20/@2026-11-23 | [175.609119, 175.194108, -0.236327, 174.321156, -0.733426] | [175.61, 175.19, -0.24, 174.32, -0.73] | 是 |
| P214 | ⑦传导链(reader_map) | TL2.verdict_note | 引擎面美元端利率高于两地 | 快照 series_store.DFEDTARU/DFEDTARL@2026-11-23 与 MRO 2.65、BOJ 目标 1.25 的大小关系 | [true, true] | [true, true] | 是 |
| P215 | ⑦传导链(reader_map) | TL2.verdict_note | 美联储 2026-09-17 生效 | 快照 series_store.DFEDTARL/DFEDTARU 最后值变更日 | ["2026-09-17", "2026-09-17"] | ["2026-09-17", "2026-09-17"] | 是 |
| P216 | ⑦传导链(reader_map) | TL2.verdict_note | 窗内三地均无政策利率变动点 | 快照 series_store.ECB_MRO/ECB_DFR/DFEDTARL/DFEDTARU 在 (2026-10-23,2026-11-20] 的变更点数; JP_POLICY_RATE 月值 2026-10→最新 | [0, 0, 0, 0, true] | [0, 0, 0, 0, true] | 是 |
| P217 | ⑦传导链(reader_map) | TL3.competing_explanation | VIX +84.5% 的单月幅度 | 快照 series_store.VIX@2026-10-23→@2026-11-20 涨跌幅% | 84.524407 | 84.5 | 是 |
| P218 | ⑦传导链(reader_map) | TL3.observed_fact | 跳升集中于末五个交易日(2026-11-13→2026-11-20,19.30→35.89) | 快照 series_store.VIX 2026-11-13 之后至 11-20 的观测数; 两值 | [5, 19.299999, 35.889999] | [5, 19.3, 35.89] | 是 |
| P219 | ⑦传导链(reader_map) | TL3.verdict_note | DAX -1.50%、CAC40 +1.86% vs SPX -9.36% | 快照 series_store.DAX/CAC40/SPX@2026-10-23→@2026-11-20 涨跌幅% | [-1.504552, 1.862181, -9.356243] | [-1.5, 1.86, -9.36] | 是 |
| P220 | ⑦传导链(reader_map) | TL3.verdict_note | 日本端与美股相当(-9.98%) | 快照 series_store.NIKKEI225@2026-10-23→@2026-11-20 涨跌幅% | -9.979574 | -9.98 | 是 |
| P221 | ⑦传导链(reader_map) | TL3.verdict_note | 距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天 | 独立推算天数差(自 2026-11-13) | [14, 58] | [14, 58] | 是 |
| P222 | ⑦传导链(reader_map) | TL3.verdict_note | 至跳升终点 2026-11-20 为 21 天、65 天 | 独立推算天数差(自 2026-11-20) | [21, 65] | [21, 65] | 是 |
| P223 | ⑦传导链(reader_map) | TL3.verdict_note | 发布当日及其后两个交易日 VIX 收盘 24.56、28.44、35.89 | 快照 series_store.VIX@2026-11-18/19/20 | [24.559999, 28.440001, 35.889999] | [24.56, 28.44, 35.89] | 是 |
| P224 | ⑦传导链(reader_map) | TL3.verdict_note | 2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7% | 快照 series_store.VIX@2026-11-23 与对 11-20 涨跌幅% | [27.01, -24.742266] | [27.01, -24.7] | 是 |
| P225 | ⑧历史类比 | HIST | S6_analog: 扫描 1871 个候选月、有效 74 | report.json steps[*].envelope(analog).data.candidates.scanned/valid | [1871, 74] | [1871, 74] | 是 |
| P226 | ⑧历史类比 | HIST | TOP1 候选月 2025-03 距离 0.727 | report.json steps[*].envelope(analog).data.top[0].{candidate_month,distance} | ["2025-03", 0.727212] | ["2025-03", 0.727] | 是 |
| P227 | ⑧历史类比 | HIST | 历史类比 0 段 | agent_judgment.json reader_map.history_periods 长度 | 0 | 0 | 是 |
| P228 | ⑨情景 | S1-STICKY-TIGHTEN.scenario | 至 2026-12 观测月(读数按引擎发布规则于 2027-01 入档,早于时限 2027-02-15) | 引擎规则独立推算: 2026-12 观测月 EA_HICP_YOY 入档日(月末+16天)与 JP_CPI_YOY 入档日(月末+20天)均 < 2027-02-15 | ["2027-01-16", "2027-01-20", true] | ["2027-01-16", "2027-01-20", true] | 是 |
| P229 | ⑨情景 | S1-STICKY-TIGHTEN.trigger | 以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;日本端两条实录可核) | release_calendar: ECB 条目数; JP_POLICY_TARGET 条目数 | [0, 2] | [0, 2] | 是 |
| P230 | ⑨情景 | S1-STICKY-TIGHTEN.trigger | VIX | VIX 日频序列在快照 series_store 在场(收盘口径可观测) | true | true | 是 |
| P231 | ⑨情景 | S2-INFL-FADE.scenario | 至 2026-12 观测月(读数按引擎发布规则于 2027-01 入档,早于时限 2027-02-15) | 引擎规则独立推算: 2026-12 观测月 EA_HICP_YOY 入档日(月末+16天)与 JP_CPI_YOY 入档日(月末+20天)均 < 2027-02-15 | ["2027-01-16", "2027-01-20", true] | ["2027-01-16", "2027-01-20", true] | 是 |
| P232 | ⑨情景 | S2-INFL-FADE.trigger | 以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;日本端两条实录可核) | release_calendar: ECB 条目数; JP_POLICY_TARGET 条目数 | [0, 2] | [0, 2] | 是 |
| P233 | ⑨情景 | S2-INFL-FADE.trigger | VIX | VIX 日频序列在快照 series_store 在场(收盘口径可观测) | true | true | 是 |
| P234 | ⑨情景 | S1-STICKY-TIGHTEN.scenario | 欧元区 HICP 同比维持 3.5% 以上 | S1.falsification.threshold 所含证伪阈(3.5%)与前提水平一致 | true | true | 是 |
| P235 | ⑨情景 | S1-STICKY-TIGHTEN.scenario | 日本全国 CPI 同比维持 2.0% 以上 | S1.trigger.condition 所含日本分量触发阈(≥2.0%)与前提一致 | true | true | 是 |
| P236 | ⑨情景 | S1-STICKY-TIGHTEN.trigger | EA_HICP_YOY 同比 ≥4.0% | S1 触发阈与证伪阈之差(触发 4.0 − 证伪 3.5,个百分点): 3.5–4.0 区间不触发亦不证伪且 S1 文本未披露该区间 | 0.5 | 0.5 | 是 |
| P237 | ⑨情景 | S1-STICKY-TIGHTEN.falsify | 若观测月 2026-11 与 2026-12 两月欧元区 HICP 同比均低于 3.5%(前提水平) | S1.falsification.threshold 是否含日本分量(JP_CPI_YOY)的数值证伪阈 | false | false | 是 |
| P238 | ⑨情景 | Q3 | S1 证伪阈值与前提水平对齐(3.5%) | S2.falsification.threshold 是否披露 3.0%–3.5% 区间 | true | true | 是 |
| P239 | ⑨情景 | S2-INFL-FADE.falsify | 或 2026-12 观测月日本全国 CPI 同比不低于 2.0% | S2.falsification.threshold 含日本分量证伪阈 | true | true | 是 |
| P240 | ⑨情景 | S2-INFL-FADE.asset | 相反 | 两情景资产方向文字: S1 含『承压/维持高位』且 S2 含『修复/回落』(方向互补) | [true, true] | [true, true] | 是 |
| P241 | ⑨情景 | S2-INFL-FADE.trigger | 低于 25 | 两情景 trigger.deadline 相同且证伪/触发指标均在注册表 | ["2027-02-15", "2027-02-15", true] | ["2027-02-15", "2027-02-15", true] | 是 |
| P242 | ⑨情景 | S2-INFL-FADE.trigger | 同时 VIX 在两读数均入档之日前最近一个交易日收盘低于 25 | 截止日下未触发亦未证伪: 2026-11 观测月两地读数按引擎规则均未入档(入档日晚于截止日) | [true, true] | [true, true] | 是 |
| P243 | ⑨情景 | S1-STICKY-TIGHTEN.falsify | (结构化字段) | 两情景 rows 五键齐备(scenario/asset_direction/sensitive_variables/falsification/trigger) | [true, true] | [true, true] | 是 |
| P244 | ⑩一致性 | report.json layers.L3_AI推断层.content | (结构化字段) | report.json L3 content 与 agent_judgment.json l3 逐键相等 | true | true | 是 |
| P245 | ⑩一致性 | report.json layers.L4_条件情景层.content | (结构化字段) | report.json L4 content 与 agent_judgment.json l4 逐键相等 | true | true | 是 |
| P246 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(矛盾陈述) | 3 | 3 | 是 |
| P247 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(矛盾陈述竞争解释) | 6 | 6 | 是 |
| P248 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(机制链四环文本) | 4 | 4 | 是 |
| P249 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(情景前提行) | 2 | 2 | 是 |
| P250 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(reader_map 标题与地区段) | 3 | 3 | 是 |
| P251 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(传导三环观察/假设/预期) | 15 | 15 | 是 |
| P252 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(转折先行/同向两栏) | 6 | 6 | 是 |
| P253 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(历史零段注记) | 1 | 1 | 是 |
| P254 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(情景证伪阈/触发条件/资产方向) | 6 | 6 | 是 |
| P255 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(传导三环对质裁定) | 3 | 3 | 是 |
| P256 | ⑩一致性 | Q0 | 共 20 条 snapshot_fact 引用,全部解析到本报告证据索引;零悬空引用 | agent_judgment.json l3 全部 evidence_refs; report.json evidence_index; 快照 series_store 是否含该指标@该日 | [20, 20, 20] | [20, 20, 20] | 是 |
| P257 | ⑦传导链 | M1.step1 | 观察: | agent_judgment.json l3.mechanism_chains[0].links[].evidence_level(观察环=E1,传导/归因环=E2) | ["E1", "E1", "E2", "E2"] | ["E1", "E1", "E2", "E2"] | 是 |
| P258 | ⑩一致性 | Q1 | 每条矛盾陈述并列 2 条(均标【假设】或如实并列) | agent_judgment.json l3.contradictions[].competing_explanations 条数与是否以【假设】起首 | [[2, 2, 2], true] | [[2, 2, 2], true] | 是 |
| P259 | ⑩一致性 | Q1 | 支持主解释 0·支持竞争解释 0·尚不能区分 3 | reader_map.transmission[0].links[].face_off_verdict 计数 | [0, 0, 3] | [0, 0, 3] | 是 |
| P260 | ⑩一致性 | agent_declaration | (结构化字段) | agent_judgment.json agent_declaration.basis 含『证据索引(60行)、点值格(6格)』; report.json evidence_index 行数; research_plan.point_values.cells 格数 | [true] | [true] | 是 |
| P261 | ⑩一致性 | agent_declaration | (结构化字段) | report.json evidence_index 行数; research_plan.point_values.cells 格数 | [60, 6] | [60, 6] | 是 |
| P262 | ⑫盘中口径 | Q4 | 快照采集于 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53、上海 22:53) | 快照 research_as_of; 独立换算四地当地时间 | ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53", "22:53"] | ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53", "22:53"] | 是 |
| P263 | ⑫盘中口径 | Q4 | SPX/VIX/DAX/CAC40 的截止日值与外汇/DXY 值均为盘中快照、非收盘价 | 快照 series_store 中 SPX/VIX/DAX/CAC40/EURUSD/USDJPY/DXY 在 2026-11-23 是否有观测; 采集时刻(纽约/柏林)早于当地收盘 | [true, true, true, true, true, true, true, true, true] | [true, true, true, true, true, true, true, true, true] | 是 |
| P264 | ⑫盘中口径 | Q4 | 席位跨地区对照统一采用 2026-11-20 同日收盘口径 | SPX/NIKKEI225/DAX/CAC40/VIX 在 2026-11-20 是否均有观测 | [true, true, true, true, true] | [true, true, true, true, true] | 是 |
| P265 | ⑬非VERIFIED披露 | Q4 | 欧央行序列止于 2026-09-16(距截止 68 天,超注册表 10 天新鲜度阈,Gate A 列 degraded | report.json agent_judgment.contract_verification.verdicts[].status 计数; 判断档全文是否出现 STALE 字样 | [1, 4, false] | [1, 4, false] | 是 |
| P266 | ⑬非VERIFIED披露 | C2 | 欧央行存款便利利率(ECB_DFR,操作下限口径)最新生效水平 2.5% | report.json contract_verification.verdicts[ECB_DFR].{token,value,expected} | [["2.5%", 2.5, 2.5]] | [["2.5%", 2.5, 2.5]] | 是 |
| P267 | ⑭缺口披露 | Q4 | JP_POLICY_TARGET 注册表不可得、宣布值仅发布日历实录 | report.json run.data_requirements.items: 六条 planned 项 outcome=insufficient_coverage 且 window.kind=unparseable(多范围无法解析); 判断档是否出现『缺口/任务目标/无法解析/多范围/降级面』字样 | [[6, ["insufficient_coverage"], ["unparseable"]], []] | [[6, ["insufficient_coverage"], ["unparseable"]], []] | 是 |
| P268 | ⑭代码缺口 | Q5 | judgment_contract._map_checks (13))锚标签硬编码「12个月前/3个月前/最新一期」 | 安装树 scripts/research_contract/judgment_contract.py: 是否存在硬编码锚标签行,及其前 60 行内是否有 (13) 注释 | [true, true] | [true, true] | 是 |
| P269 | ⑭代码缺口 | Q5 | 本问锚为「6个月前/最新一期」 | report.json research_plan.point_anchors[].label | ["6个月前", "最新一期"] | ["6个月前", "最新一期"] | 是 |
| P270 | ⑭代码缺口 | Q5 | text_consistency.ALIASES 静态别名表未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO | 安装树 scripts/research_contract/text_consistency.py ALIASES 键是否含上述五指标 | [false, false, false, false, false] | [false, false, false, false, false] | 是 |
| P271 | ⑭代码缺口 | Q5 | 带别名指标的最新值带指标 id 由契约逐位核验 | ALIASES 含 CPI; 契约验证 verdicts 的 metric 均为 ALIASES 键 | [true, ["ECB_DFR", "JP_POLICY_RATE", "SPX", "USDJPY", "VIX"], true] | [true, ["ECB_DFR", "JP_POLICY_RATE", "SPX", "USDJPY", "VIX"], true] | 是 |
| P272 | ⑭代码缺口 | Q5 | 引擎报告文字「观测日全为周三」对变更点序列表述过宽(两序列含非周三观测) | MAP_REPORT.md 含该文字; 两序列非周三观测数 | [true, 9, 21] | [true, 9, 21] | 是 |
| P273 | ⑩一致性 | report.json layers.L3_AI推断层.content | (结构化字段) | report.json L3 content 与 agent_judgment.json l3 逐键相等 | true | true | 是 |
| P274 | ⑩一致性 | report.json layers.L4_条件情景层.content | (结构化字段) | report.json L4 content 与 agent_judgment.json l4 逐键相等 | true | true | 是 |
| P275 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(矛盾陈述) | 3 | 3 | 是 |
| P276 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(矛盾陈述竞争解释) | 6 | 6 | 是 |
| P277 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(机制链四环文本) | 4 | 4 | 是 |
| P278 | ⑩一致性 | FULL_REPORT.md/report.md | (结构化字段) | FULL_REPORT.md/report.md 逐字包含判断档字符串数(情景前提行) | 2 | 2 | 是 |
| P279 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(reader_map 标题与地区段) | 3 | 3 | 是 |
| P280 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(传导三环观察/假设/预期) | 15 | 15 | 是 |
| P281 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(转折先行/同向两栏) | 6 | 6 | 是 |
| P282 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(历史零段注记) | 1 | 1 | 是 |
| P283 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(情景证伪阈/触发条件/资产方向) | 6 | 6 | 是 |
| P284 | ⑩一致性 | MAP_REPORT.md | (结构化字段) | MAP_REPORT.md 逐字包含判断档字符串数(传导三环对质裁定) | 3 | 3 | 是 |
| P285 | ⑩一致性 | Q0 | 共 20 条 snapshot_fact 引用,全部解析到本报告证据索引;零悬空引用 | agent_judgment.json l3 全部 evidence_refs; report.json evidence_index; 快照 series_store 是否含该指标@该日 | [20, 20, 20] | [20, 20, 20] | 是 |
| P286 | ⑦传导链 | M1.step1 | 观察: | agent_judgment.json l3.mechanism_chains[0].links[].evidence_level(观察环=E1,传导/归因环=E2) | ["E1", "E1", "E2", "E2"] | ["E1", "E1", "E2", "E2"] | 是 |
| P287 | ⑩一致性 | Q1 | 每条矛盾陈述并列 2 条(均标【假设】或如实并列) | agent_judgment.json l3.contradictions[].competing_explanations 条数与是否以【假设】起首 | [[2, 2, 2], true] | [[2, 2, 2], true] | 是 |
| P288 | ⑩一致性 | Q1 | 支持主解释 0·支持竞争解释 0·尚不能区分 3 | reader_map.transmission[0].links[].face_off_verdict 计数 | [0, 0, 3] | [0, 0, 3] | 是 |
| P289 | ⑩一致性 | agent_declaration | (结构化字段) | agent_judgment.json agent_declaration.basis 含『证据索引(60行)、点值格(6格)』; report.json evidence_index 行数; research_plan.point_values.cells 格数 | [true] | [true] | 是 |
| P290 | ⑩一致性 | agent_declaration | (结构化字段) | report.json evidence_index 行数; research_plan.point_values.cells 格数 | [60, 6] | [60, 6] | 是 |
| P291 | ⑫盘中口径 | Q4 | 快照采集于 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53、上海 22:53) | 快照 research_as_of; 独立换算四地当地时间 | ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53", "22:53"] | ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53", "22:53"] | 是 |
| P292 | ⑫盘中口径 | Q4 | SPX/VIX/DAX/CAC40 的截止日值与外汇/DXY 值均为盘中快照、非收盘价 | 快照 series_store 中 SPX/VIX/DAX/CAC40/EURUSD/USDJPY/DXY 在 2026-11-23 是否有观测; 采集时刻(纽约/柏林)早于当地收盘 | [true, true, true, true, true, true, true, true, true] | [true, true, true, true, true, true, true, true, true] | 是 |
| P293 | ⑫盘中口径 | Q4 | 席位跨地区对照统一采用 2026-11-20 同日收盘口径 | SPX/NIKKEI225/DAX/CAC40/VIX 在 2026-11-20 是否均有观测 | [true, true, true, true, true] | [true, true, true, true, true] | 是 |
| P294 | ⑬非VERIFIED披露 | Q4 | 欧央行序列止于 2026-09-16(距截止 68 天,超注册表 10 天新鲜度阈,Gate A 列 degraded | report.json agent_judgment.contract_verification.verdicts[].status 计数; 判断档全文是否出现 STALE 字样 | [1, 4, false] | [1, 4, false] | 是 |
| P295 | ⑬非VERIFIED披露 | C2 | 欧央行存款便利利率(ECB_DFR,操作下限口径)最新生效水平 2.5% | report.json contract_verification.verdicts[ECB_DFR].{token,value,expected} | [["2.5%", 2.5, 2.5]] | [["2.5%", 2.5, 2.5]] | 是 |
| P296 | ⑭缺口披露 | Q4 | JP_POLICY_TARGET 注册表不可得、宣布值仅发布日历实录 | report.json run.data_requirements.items: 六条 planned 项 outcome=insufficient_coverage 且 window.kind=unparseable(多范围无法解析); 判断档是否出现『缺口/任务目标/无法解析/多范围/降级面』字样 | [[6, ["insufficient_coverage"], ["unparseable"]], []] | [[6, ["insufficient_coverage"], ["unparseable"]], []] | 是 |
| P297 | ⑭代码缺口 | Q5 | judgment_contract._map_checks (13))锚标签硬编码「12个月前/3个月前/最新一期」 | 安装树 scripts/research_contract/judgment_contract.py: 是否存在硬编码锚标签行,及其前 60 行内是否有 (13) 注释 | [true, true] | [true, true] | 是 |
| P298 | ⑭代码缺口 | Q5 | 本问锚为「6个月前/最新一期」 | report.json research_plan.point_anchors[].label | ["6个月前", "最新一期"] | ["6个月前", "最新一期"] | 是 |
| P299 | ⑭代码缺口 | Q5 | text_consistency.ALIASES 静态别名表未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO | 安装树 scripts/research_contract/text_consistency.py ALIASES 键是否含上述五指标 | [false, false, false, false, false] | [false, false, false, false, false] | 是 |
| P300 | ⑭代码缺口 | Q5 | 带别名指标的最新值带指标 id 由契约逐位核验 | ALIASES 含 CPI; 契约验证 verdicts 的 metric 均为 ALIASES 键 | [true, ["ECB_DFR", "JP_POLICY_RATE", "SPX", "USDJPY", "VIX"], true] | [true, ["ECB_DFR", "JP_POLICY_RATE", "SPX", "USDJPY", "VIX"], true] | 是 |
| P301 | ⑭代码缺口 | Q5 | 引擎报告文字「观测日全为周三」对变更点序列表述过宽(两序列含非周三观测) | MAP_REPORT.md 含该文字; 两序列非周三观测数 | [true, 9, 21] | [true, 9, 21] | 是 |
