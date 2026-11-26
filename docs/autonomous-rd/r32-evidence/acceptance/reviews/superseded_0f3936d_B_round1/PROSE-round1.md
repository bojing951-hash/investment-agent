# 独立语义审查席位复算记录(Audit-R32 正式使用验收 · B · Round-1)

- 席位: semantic-audit-seat / independent-zero-context-seat-r32-b-round1(零上下文;与研判席、操作席零通信)
- 裁决日: 2026-11-24
- 受审对象: 运行目录 `20261123T193157Z_对比角度换一个_…`(代码印章 0f3936dd7eb74c557a2350e400d58e10a09c5139)内 `agent_judgment.json` 全文(l3 / l4 / reader_map / quality_gate_notes / agent_declaration)与读者报告中的判断文字(`MAP_REPORT.md` / `FULL_REPORT.md` / `report.md`)
- 工单原文: 「对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？」
- 只读面: 冻结快照 `root_overlay/data/daily/research_snapshot_20261123.json`(series_store 92 序列 / facts 105 / gate_a)、冻结日历 `root_overlay/config/release_calendar.json`(v1.5.0)、注册表 `root_overlay/config/metric_registry.json`、引擎运行档 `report.json` / `evidence_index.json` / `AGENT_SEAT_ENVELOPE.json`、安装树内引擎发布规则表源码行 `scripts/research_map_planner.py` 的 `RELEASE_RULES`(只读取文本,未执行任何引擎命令)
- 复算脚本(均在本目录,经 `/usr/bin/python3 -I` 运行,路径作参数传入): `s10_recompute.py`(主复算 190 点)、`s12_build_prose.py`(由复算结果生成本文件第 2 节)、`s13_build_verdict.py`(由复算结果生成 `VERDICT-round1.json`)、`s14_check_originals.py`(核验裁决档所引原句逐字在场)、`s01`–`s06` / `s11_probe.py`(结构探针与逐字抽取)。逐点明细另存 `recompute_points.json` / `recompute_points.txt`。
- 独立性声明: 未读取规程第 2 节所列任何目录;未联网;未运行任何写操作;未索取、推测或依赖任何预审内容;未委派子代理。

## 0. 裁决速览

| 项 | 结果 |
|---|---|
| 裁决 | **REVISE** |
| recompute_points / recompute_mismatches | 190 / 1 |
| MAJOR / MINOR / NIT | 1 / 5 / 10 |
| 必修 | MAJOR-1:S1-INFL-STICKY 证伪阈值句按字面不可触发 |

数值面结论: 全部点值锚、同比基期、政策日历条目与天数、三利率分解、资产月窗、转折候选池、Gate A 与 STALE 披露均与冻结快照 / 冻结日历 / 引擎面逐位一致;唯一偏离是情景 S1 的证伪条件(期限与截止日读数不相容,见第 5 节)。

## 1. 复算方法与覆盖

- 计数: 190 点中 186 点归入规程第 3 节的①–⑭(①10 ②39 ③24 ④17 ⑤41 ⑥9 ⑦1 ⑧2 ⑨8 ⑩10 ⑪15 ⑫2 ⑬4 ⑭4),4 点归入第 4 节六查的在场对照(竞争解释与反对证据)。
- 口径: 被比对值取自报告或判断档文字(含引擎面数值与披露声明)的 178 点;报告工件完整性 / 渲染核验 4 点(M2–M5);席位补充探测 8 点(E12、I5、I6、J0、K2、K4、K5、K6——判断档未载数值,只记录直算面,供六查与反方攻击引用)。
- 方法: 每个被引数值先从 series_store 直算(锚格取「锚 as_of 当日或之前最后已发布观测」,发布可见性按引擎发布规则推定日逐格核对)、再与冻结日历条目和 report.json 引擎面对照、最后与判断档 / 报告文字按其显示精度逐位比对;同比一律取去年同月 / 同季基期;利率分解按共同交易日窗核「名义=实际+盈亏平衡」;日频变动按报告所载两端点日期与值比对。
- 反方核(报告未给出、席位另算以防其以相邻口径冒充): CPI 2026-10 若以相邻月 2025-11 为基期会得 3.82%,报告未使用该口径而如实标「不可得」(B17b);SPX 共同窗(2026-10-23→2026-11-19)−5.87%(E12)。

## 2. 逐点复算清单

命中 189 / 偏离 1(共 190 点)。「直算值」=席位自冻结快照 / 冻结日历 / 引擎面独立计算;「报告值」=判断档或报告所载(含披露声明);「结果」=一致 或 **偏离**。

### ① 截止日与观测 / 发布日不晚于截止日(10 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| A1-cutoff-report | report.run.evidence_gate.as_of / MAP_REPORT header | 2026-11-23 | 2026-11-23 | 一致 |  |
| A2-cutoff-snapshot | root_overlay/data/daily/research_snapshot_20261123.json:target_date | 20261123 | 20261123 | 一致 |  |
| A3-asof-claim | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of | 2026-11-23T22:53:47+08:00 | 2026-11-23T22:53:47+08:00 | 一致 |  |
| A4-local-clocks | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of (UTC+0 固定标准时偏移换算) | {"纽约": "09:53", "法兰克福": "15:53", "东京": "23:53", "上海": "22:53"} | {"纽约": "09:53", "法兰克福": "15:53", "东京": "23:53", "上海": "22:53"} | 一致 | 11 月纽约=EST(-5)/法兰克福=CET(+1),由 22:53:47+08:00=14:53:47Z 换算 |
| A5-no-post-cutoff-obs | root_overlay/data/daily/research_snapshot_20261123.json:series_store[*].dates max | 2026-11-23 | <=2026-11-23 | 一致 |  |
| A5b-late-series-count | root_overlay/data/daily/research_snapshot_20261123.json:series_store (date>2026-11-23) | 0 | 0 | 一致 |  |
| A6-cited-last-obs-dates | root_overlay/data/daily/research_snapshot_20261123.json:series_store[*] last date | {"SPX": "2026-11-23", "VIX": "2026-11-23", "GOLD_F": "2026-11-23", "DXY": "2026-11-23", "USDJPY": "2026-11-23", "NIKKEI225": "2026-11-20", "BEI_10Y": "2026-11-20", "TIPS_10Y": "2026-11-19", "UST_10Y": "2026-11-19", "EA_HICP_YOY": "2026-10-01", "CPI": "2026-10-01", "CORE_CPI": "2026-10-01", "INDPRO": "2026-10-01", "UNEMPLOYMENT": "2026-10-01", "JP_POLICY_RATE": "2026-10-01", "CORE_PCE": "2026-09-01", "US_REAL_GDP": "2026-07-01", "EA_REAL_GDP_YOY": "2026-07-01"} | {"SPX": "2026-11-23", "VIX": "2026-11-23", "GOLD_F": "2026-11-23", "DXY": "2026-11-23", "USDJPY": "2026-11-23", "NIKKEI225": "2026-11-20", "BEI_10Y": "2026-11-20", "TIPS_10Y": "2026-11-19", "UST_10Y": "2026-11-19", "EA_HICP_YOY": "2026-10-01", "CPI": "2026-10-01", "CORE_CPI": "2026-10-01", "INDPRO": "2026-10-01", "UNEMPLOYMENT": "2026-10-01", "JP_POLICY_RATE": "2026-10-01", "CORE_PCE": "2026-09-01", "US_REAL_GDP": "2026-07-01", "EA_REAL_GDP_YOY": "2026-07-01"} | 一致 |  |
| A7-anchor-publication<=anchor-asof | report.research_plan.point_values.cells[*].anchors.*.publication_date vs as_of | {"US_REAL_GDP\|3个月前": ["2026-04-01", "2026-07-29", "2026-08-23"], "US_REAL_GDP\|最新一期": ["2026-07-01", "2026-10-29", "2026-11-23"], "UNEMPLOYMENT\|3个月前": ["2026-07-01", "2026-08-05", "2026-08-23"], "UNEMPLOYMENT\|最新一期": ["2026-10-01", "2026-11-05", "2026-11-23"], "INDPRO\|3个月前": ["2026-07-01", "2026-08-15", "2026-08-23"], "INDPRO\|最新一期": ["2026-10-01", "2026-11-15", "2026-11-23"], "CPI\|3个月前": ["2026-07-01", "2026-08-13", "2026-08-23"], "CPI\|最新一期": ["2026-10-01", "2026-11-13", "2026-11-23"], "CORE_CPI\|3个月前": ["2026-07-01", "2026-08-13", "2026-08-23"], "CORE_CPI\|最新一期": ["2026-10-01", "2026-11-13", "2026-11-23"], "CORE_PCE\|3个月前": ["2026-06-01", "2026-07-30", "2026-08-23"], "CORE_PCE\|最新一期": ["2026-09-01", "2026-10-30", "2026-11-23"], "EA_REAL_GDP_YOY\|3个月前": ["2026-04-01", "2026-08-04", "2026-08-23"], "EA_REAL_GDP_YOY\|最新一期": ["2026-07-01", "2026-11-04", "2026-11-23"], "EA_HICP_YOY\|3个月前": ["2026-07-01", "2026-08-16", "2026-08-23"], "EA_HICP_YOY\|最新一期": ["2026-10-01", "2026-11-16", "2026-11-23"], "JP_POLICY_RATE\|3个月前": ["2026-07-01", "2026-08-05", "2026-08-23"], "JP_POLICY_RATE\|最新一期": ["2026-10-01", "2026-11-05", "2026-11-23"]} | all publication_date<=as_of | 一致 |  |
| A8-publication-rule-arithmetic | period_end + 规则天数 vs engine publication_date | {"US_REAL_GDP\|3个月前": ["2026-07-29", "2026-07-29"], "US_REAL_GDP\|最新一期": ["2026-10-29", "2026-10-29"], "UNEMPLOYMENT\|3个月前": ["2026-08-05", "2026-08-05"], "UNEMPLOYMENT\|最新一期": ["2026-11-05", "2026-11-05"], "INDPRO\|3个月前": ["2026-08-15", "2026-08-15"], "INDPRO\|最新一期": ["2026-11-15", "2026-11-15"], "CPI\|3个月前": ["2026-08-13", "2026-08-13"], "CPI\|最新一期": ["2026-11-13", "2026-11-13"], "CORE_CPI\|3个月前": ["2026-08-13", "2026-08-13"], "CORE_CPI\|最新一期": ["2026-11-13", "2026-11-13"], "CORE_PCE\|3个月前": ["2026-07-30", "2026-07-30"], "CORE_PCE\|最新一期": ["2026-10-30", "2026-10-30"], "EA_REAL_GDP_YOY\|3个月前": ["2026-08-04", "2026-08-04"], "EA_REAL_GDP_YOY\|最新一期": ["2026-11-04", "2026-11-04"], "EA_HICP_YOY\|3个月前": ["2026-08-16", "2026-08-16"], "EA_HICP_YOY\|最新一期": ["2026-11-16", "2026-11-16"], "JP_POLICY_RATE\|3个月前": ["2026-08-05", "2026-08-05"], "JP_POLICY_RATE\|最新一期": ["2026-11-05", "2026-11-05"]} | 逐项相等 | 一致 |  |
| M2-map-sha-anchor | MAP_REPORT.sha256 vs sha256(MAP_REPORT.md) | ["e1e13eb95ec77e7f", "e1e13eb95ec77e7f"] | 相等 | 一致 |  |

### ② 点值锚格(39 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| B1-GDP-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP@2026-04-01 | 24408.011 | 24408.011 | 一致 |  |
| B2-GDP-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP@2026-07-01 | 24611.077 | 24611.077 | 一致 |  |
| B5-UNEMP-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT@2026-07-01 | 4.1 | 4.1 | 一致 |  |
| B6-UNEMP-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT@2026-10-01 | 4.1 | 4.1 | 一致 |  |
| B7-INDPRO-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO@2026-07-01 | 103.1675 | 103.1675 | 一致 |  |
| B8-INDPRO-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO@2026-10-01 | 103.3954 | 103.3954 | 一致 |  |
| B14-CPI-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI@2026-07-01 | 332.813 | 332.813 | 一致 |  |
| B15-CPI-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI@2026-10-01 | 337.476 | 337.476 | 一致 |  |
| B19-CCPI-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI@2026-07-01 | 336.789 | 336.789 | 一致 |  |
| B20-CCPI-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI@2026-10-01 | 339.9 | 339.9 | 一致 |  |
| B24-CPCE-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE@2026-06-01 | 129.969 | 129.969 | 一致 |  |
| B25-CPCE-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE@2026-09-01 | 130.902 | 130.902 | 一致 |  |
| B25b-CPCE-3m-anchor-month | CORE_PCE 2026-07 观测在库值 / 规则发布日(月末+30) vs 3个月前锚 as_of | {"CPCE@2026-07": 130.148, "pub_2026-07": "2026-08-30", "pub_2026-06": "2026-07-30", "anchor_as_of": "2026-08-23", "engine_anchor_obs": "2026-06-01"} | {"CPCE@2026-07": 130.148, "pub_2026-07": "2026-08-30", "pub_2026-06": "2026-07-30", "anchor_as_of": "2026-08-23", "engine_anchor_obs": "2026-06-01"} | 一致 | 2026-07 观测在库但 2026-08-30 才发布(晚于锚 as_of 2026-08-23)→3个月前锚取 2026-06 与引擎格一致(可见性口径,非缺席口径;席位首版此检以『观测缺席』为假设有误,已更正) |
| B28-EAGDP-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY@2026-04-01 | 1.19 | 1.19 | 一致 |  |
| B29-EAGDP-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY@2026-07-01 | 1.28 | 1.28 | 一致 |  |
| B30-EAHICP-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY@2026-07-01 | 2.9 | 2.9 | 一致 |  |
| B31-EAHICP-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY@2026-10-01 | 4.0 | 4.0 | 一致 |  |
| B33-EAHICP-2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY@2026-02-01 | 1.9 | 1.9 | 一致 |  |
| B34-EAHICP-2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY@2026-05-01 | 3.2 | 3.2 | 一致 |  |
| B35-EAHICP-2026-06 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY@2026-06-01 | 2.8 | 2.8 | 一致 |  |
| B36b-EAHICP-2026-path | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY 2026 全年 | [["2026-01", 1.7], ["2026-02", 1.9], ["2026-03", 2.6], ["2026-04", 3.0], ["2026-05", 3.2], ["2026-06", 2.8], ["2026-07", 2.9], ["2026-08", 3.2], ["2026-09", 3.8], ["2026-10", 4.0]] | 见 note | 一致 | 2026-01=1.7; 2026-02=1.9; 2026-03=2.6; 2026-04=3.0; 2026-05=3.2; 2026-06=2.8; 2026-07=2.9; 2026-08=3.2; 2026-09=3.8; 2026-10=4.0 |
| B37-JPR-3m | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-07-01 | 0.978 | 0.978 | 一致 |  |
| B38-JPR-latest | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-10-01 | 1.227 | 1.227 | 一致 |  |
| B39-JPR-step-2025-11 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2025-11-01 | 0.478 | 0.478 | 一致 |  |
| B39-JPR-step-2025-12 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2025-12-01 | 0.557 | 0.557 | 一致 |  |
| B39-JPR-step-2026-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-01-01 | 0.728 | 0.728 | 一致 |  |
| B39-JPR-step-2026-04 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-04-01 | 0.727 | 0.727 | 一致 |  |
| B39-JPR-step-2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-05-01 | 0.727 | 0.727 | 一致 |  |
| B39-JPR-step-2026-06 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-06-01 | 0.841 | 0.841 | 一致 |  |
| B39-JPR-step-2026-08 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-08-01 | 0.977 | 0.977 | 一致 |  |
| B39-JPR-step-2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE@2026-09-01 | 1.043 | 1.043 | 一致 |  |
| B40-JPR-full-path | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE 2025-10..2026-10 | [["2025-10", 0.477], ["2025-11", 0.478], ["2025-12", 0.557], ["2026-01", 0.728], ["2026-02", 0.728], ["2026-03", 0.728], ["2026-04", 0.727], ["2026-05", 0.727], ["2026-06", 0.841], ["2026-07", 0.978], ["2026-08", 0.977], ["2026-09", 1.043], ["2026-10", 1.227]] | 见 note | 一致 | 2025-10=0.477; 2025-11=0.478; 2025-12=0.557; 2026-01=0.728; 2026-02=0.728; 2026-03=0.728; 2026-04=0.727; 2026-05=0.727; 2026-06=0.841; 2026-07=0.978; 2026-08=0.977; 2026-09=1.043; 2026-10=1.227 |
| B47-JPR-step-deltas | JP_POLICY_RATE 相邻月均差 (bp) | {"2025-12": 8, "2026-01": 17, "2026-06": 11, "2026-07": 14, "2026-09": 7, "2026-10": 18} | {"2025-12": 8, "2026-01": 17, "2026-06": 11, "2026-07": 14, "2026-09": 7, "2026-10": 18} | 一致 |  |
| E6-USDJPY | series_store.USDJPY@2026-11-23 | 159.347 | 159.35 | 一致 |  |
| F2b-CPI-yoy-2026-path | CPI 同比 2026 逐月 | [["2026-01", 2.3912], ["2026-02", 2.434], ["2026-03", 3.286], ["2026-04", 3.7792], ["2026-05", 4.1666], ["2026-06", 3.4635], ["2026-07", 3.3039], ["2026-08", 3.353], ["2026-09", 3.7173], ["2026-10", null]] | 见 note | 一致 | 2026-01=2.3912; 2026-02=2.434; 2026-03=3.286; 2026-04=3.7792; 2026-05=4.1666; 2026-06=3.4635; 2026-07=3.3039; 2026-08=3.353; 2026-09=3.7173; 2026-10=None |
| F3b-CCPI-yoy-2026-path | CORE_CPI 同比 2026 逐月 | [["2026-01", 2.512], ["2026-02", 2.4725], ["2026-03", 2.6022], ["2026-04", 2.7433], ["2026-05", 2.8229], ["2026-06", 2.5658], ["2026-07", 2.4665], ["2026-08", 2.4462], ["2026-09", 2.5658], ["2026-10", null]] | 见 note | 一致 | 2026-01=2.512; 2026-02=2.4725; 2026-03=2.6022; 2026-04=2.7433; 2026-05=2.8229; 2026-06=2.5658; 2026-07=2.4665; 2026-08=2.4462; 2026-09=2.5658; 2026-10=None |
| F6-UNEMP-05-08 | UNEMPLOYMENT @2026-05-01 / @2026-08-01 | [4.3, 4.1] | [4.3, 4.1] | 一致 |  |
| I2-point-cells | report.research_plan.point_values.cells 长度 | 9 | 9 | 一致 | agent_declaration「点值格(9格)」 |
| I4-anchor-echo-vs-grid | agent_judgment.reader_map.regions[*].anchor_echo vs report.research_plan.point_values.cells[*].anchors | 18/18 | 18/18 值与观测月一致 | 一致 |  |

### ③ 同比基期与最近有效同比(24 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| B3-GDP-yoy-Q2 | series_store.US_REAL_GDP 24408.011 / 23884.563 | 2.1915745328897174 | 2.19 | 一致 | 基期=2025-04-01 同季 |
| B4-GDP-yoy-Q3 | series_store.US_REAL_GDP 24611.077 / 24112.966 | 2.0657392375537764 | 2.07 | 一致 | 基期=2025-07-01 同季 |
| B9-INDPRO-yoy-07 | series_store.INDPRO 103.1675 / 101.894 | 1.2498282528902616 | 1.25 | 一致 | 基期=2025-07-01 同月 |
| B10-INDPRO-yoy-10 | series_store.INDPRO 103.3954 / 101.2195 | 2.1496845963475453 | 2.15 | 一致 | 基期=2025-10-01 同月 |
| B16-CPI-yoy-07 | series_store.CPI 332.813 / 322.169 | 3.303856050706311 | 3.3 | 一致 | 基期=2025-07-01 同月 |
| B17-CPI-yoy-10-NA | series_store.CPI 2026-10 与 2025-10 | {"yoy": null, "pair": [337.476, null]} | 不可得(缺2025-10基期) | 一致 |  |
| B17b-CPI-yoy-10-if-substituted | CPI 2026-10 / 2025-11 (相邻月替代口径,报告未使用) | 3.82 | 报告未给出该数 | 一致 | 反方核: 若以相邻月替代会得 3.82%, 报告如实标不可得 |
| B18-CPI-latest-valid-yoy | series_store.CPI 336.298 / 324.245 | {"date": "2026-09-01", "yoy": 3.7173} | {"date": "2026-09-01", "yoy": 3.72} | 一致 | 最近有效同比=2026-09 |
| B18b-CPI-latest-valid-is-09 | series_store.CPI 最后观测=2026-10(同比不可得) | 2026-10-01 | 2026-10-01 | 一致 |  |
| B21-CCPI-yoy-07 | series_store.CORE_CPI 336.789 / 328.682 | 2.4665177892309265 | 2.47 | 一致 | 基期=2025-07-01 同月 |
| B22-CCPI-yoy-10-NA | series_store.CORE_CPI 2026-10 与 2025-10 | {"yoy": null, "pair": [339.9, null]} | 不可得(缺2025-10基期) | 一致 |  |
| B23-CCPI-latest-valid-yoy | series_store.CORE_CPI 338.896 / 330.418 | {"date": "2026-09-01", "yoy": 2.5658} | {"date": "2026-09-01", "yoy": 2.57} | 一致 | 最近有效同比=2026-09 |
| B26-CPCE-yoy-06 | series_store.CORE_PCE 129.969 / 126.133 | 3.041234252733216 | 3.04 | 一致 | 基期=2025-06-01 同月 |
| B27-CPCE-yoy-09 | series_store.CORE_PCE 130.902 / 126.94 | 3.1211596029620203 | 3.12 | 一致 | 基期=2025-09-01 同月 |
| F1-CPI-yoy-02 | CPI 2026-02 / 2025-02 | 2.434 | 2.434 | 一致 |  |
| F1-CPI-yoy-05 | CPI 2026-05 / 2025-05 | 4.1666 | 4.1666 | 一致 |  |
| F3-CCPI-yoy-2026-02 | CORE_CPI 2026-02 / 上年同月 | 2.4725 | 2.4725 | 一致 |  |
| F3-CCPI-yoy-2026-05 | CORE_CPI 2026-05 / 上年同月 | 2.8229 | 2.8229 | 一致 |  |
| F3-CCPI-yoy-2026-08 | CORE_CPI 2026-08 / 上年同月 | 2.4462 | 2.4462 | 一致 |  |
| F3-CCPI-yoy-2026-09 | CORE_CPI 2026-09 / 上年同月 | 2.5658 | 2.5658 | 一致 |  |
| F4-INDPRO-yoy-2025-11 | INDPRO 2025-11 / 2024-11 | 1.7543 | 1.7543 | 一致 |  |
| F4-INDPRO-yoy-2026-02 | INDPRO 2026-02 / 2025-02 | 0.7972 | 0.7972 | 一致 |  |
| F5-CPCE-yoy-2025-11 | CORE_PCE 2025-11 / 2024-11 | 2.7212 | 2.7212 | 一致 |  |
| F5-CPCE-yoy-2026-02 | CORE_PCE 2026-02 / 2025-02 | 2.9592 | 2.9592 | 一致 |  |

### ④ 政策面(17 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| C1-BOJ-decision | release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date | 2026-09-18 | 2026-09-18 | 一致 |  |
| C2-BOJ-effective | release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].effective_on | 2026-09-24 | 2026-09-24 | 一致 |  |
| C3-BOJ-target | release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].target_value | 1.25 | 1.25 | 一致 |  |
| C4-BOJ-maintain | release_calendar.entries[RC-JP-BOJ-MAINT-2026-10] | {"decision_date": "2026-10-30", "target_value": 1.25, "kind": "policy_maintenance"} | {"decision_date": "2026-10-30", "target_value": 1.25, "kind": "policy_maintenance"} | 一致 |  |
| C5-days-effective | 2026-11-23 − 2026-09-24 | 60 | 60 | 一致 |  |
| C6-days-decision | 2026-11-23 − 2026-09-18 | 66 | 66 | 一致 |  |
| C7-days-maintain | 2026-11-23 − 2026-10-30 (MAP 官方记录面「距维持」) | 24 | 24 | 一致 |  |
| C8-policy-entries | release_calendar.entries kind=policy_* | [["RC-JP-BOJ-TARGET-2026-09", "2026-09-18"], ["RC-JP-BOJ-MAINT-2026-10", "2026-10-30"]] | 2 条,均日本央行 | 一致 |  |
| C8b-no-later-boj | release_calendar JP_POLICY_TARGET 条目 decision_date 最大值 | 2026-10-30 | 2026-10-30 | 一致 | 「此后是否有新决议引擎日历无条目」 |
| C10-calendar-version | release_calendar.version | 1.5.0 | v1.5.0 | 一致 |  |
| C12-JPR-registry-name | metric_registry JP_POLICY_RATE.display_name | 日本无担保隔夜拆借利率(月均) | 日本无担保隔夜拆借利率(月均) | 一致 |  |
| C13-first-full-month | 生效日 2026-09-24 之后首个整月 | 2026-10 | 2026-10 | 一致 | 9-24 生效→10 月为首个整月;月均台阶落在 2026-09→2026-10 之交 |
| C14-FOMC-minutes | report.research_plan.policy_doc_facts | [["FOMC-MINUTES-2026-10", "2026-11-18"]] | [["FOMC-MINUTES-2026-10", "2026-11-18"]] | 一致 |  |
| C14b-minutes<=cutoff | FOMC 纪要发布日 ≤ 研究截止日 | true | true | 一致 |  |
| C15-policy-clusters-empty | report.research_plan.policy_event_clusters.clusters | [] | [] | 一致 |  |
| E12-SPX-common-to-1119 | SPX 2026-11-19 / 2026-10-23 (7623.680176→7175.830078) | -5.8745 | 未载(席位补充核) | 一致 | 反方核: 与 TIPS_10Y 同止于 11-19 的 SPX 同窗跌幅 |
| I3-maintain-no-effective | release_calendar.entries[RC-JP-BOJ-MAINT-2026-10] 是否含 effective_on 键 | false | false | 一致 | 「维持条目无生效日,正文不为其挂生效日」 |

### ⑤ 三利率分解与资产月窗(41 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| B45-JPR-net-engine | JP_POLICY_RATE 2026-10 − 2025-12 (bp) | 67.0 | 67 | 一致 | 引擎政策窗口径(窗首观测 2025-12) |
| B46-JPR-net-alt | JP_POLICY_RATE 2026-10 − 2025-11 (bp) | 74.9 | 75 | 一致 | 窗启时在值口径 |
| D1-UST-1m-bp | UST_10Y 2026-11-19 − 2026-10-20 (5.12→5.04) | -8.0 | -8 | 一致 |  |
| D2-TIPS-1m-bp | TIPS_10Y 2026-11-19 − 2026-10-20 (2.77→2.88) | 11.0 | 11 | 一致 |  |
| D3-BEI-1m-bp | BEI_10Y 2026-11-19 − 2026-10-20 (2.35→2.16) | -19.0 | -19 | 一致 |  |
| D4-identity-1m | 名义 − (实际+盈亏平衡) | -0.0 | 0 | 一致 | 残差 0 |
| D5-levels-1119 | UST_10Y/TIPS_10Y/BEI_10Y @2026-11-19 | [5.04, 2.88, 2.16] | [5.04, 2.88, 2.16] | 一致 |  |
| D5b-BEI-level-1120 | BEI_10Y@2026-11-20 | 2.15 | 2.15 | 一致 |  |
| D6-UST-3m-bp | UST_10Y 2026-11-19 − 2026-08-19 (4.65→5.04) | 39.0 | 39 | 一致 |  |
| D6-TIPS-3m-bp | TIPS_10Y 2026-11-19 − 2026-08-19 (2.35→2.88) | 53.0 | 53 | 一致 |  |
| D6-BEI-3m-bp | BEI_10Y 2026-11-19 − 2026-08-19 (2.3→2.16) | -14.0 | -14 | 一致 |  |
| D6-identity-3m | 名义 − (实际+盈亏平衡) | -0.0 | 0 | 一致 | 残差 0 |
| D8-BEI-3m-from | BEI_10Y@2026-08-19 | 2.3 | 2.3 | 一致 | 「自 2.30 回落至 2.16」 |
| D7-UST-12m-bp | UST_10Y 2026-11-19 − 2025-11-19 (4.13→5.04) | 91.0 | 91 | 一致 |  |
| D7-TIPS-12m-bp | TIPS_10Y 2026-11-19 − 2025-11-19 (1.86→2.88) | 102.0 | 102 | 一致 |  |
| D7-BEI-12m-bp | BEI_10Y 2026-11-19 − 2025-11-19 (2.27→2.16) | -11.0 | -11 | 一致 |  |
| D7-identity-12m | 名义 − (实际+盈亏平衡) | 0.0 | 0 | 一致 | 残差 0 |
| D7b-days-12m | 日历日间隔 2025-11-19→2026-11-19 | 365 | 365 | 一致 |  |
| D6b-days-1m | 日历日间隔 2026-10-20→2026-11-19 | 30 | 30 | 一致 |  |
| D10-BEI-12m-min | BEI_10Y [2025-11-19..2026-11-20] 最小值 | {"min": 2.15, "at": ["2026-11-20"], "n": 252} | {"min": 2.15, "at": ["2026-11-20"]} | 一致 | 「12 个月窗内最低」 |
| D11-BEI-0227 | BEI_10Y@2026-02-27 | 2.25 | 2.25 | 一致 |  |
| D11-BEI-0504 | BEI_10Y@2026-05-04 | 2.5 | 2.5 | 一致 |  |
| D11b-BEI-engine-30d | BEI_10Y 2026-11-20 − 2026-10-23 (2.34→2.15) | [-19.0, 2.34, 2.15] | [-19, 2.34, 2.15] | 一致 | MAP 对质表引擎面「近30日2.34→2.15,下降19bp」= fact m1 窗(席位首版此检误用 2026-10-21 起点得 -22bp,已更正为引擎窗) |
| D12-TIPS-1023 | TIPS_10Y 2026-11-19 − 2026-10-23 (2.66→2.88) | 22.0 | 22 | 一致 | 「同窗 TIPS_10Y 2.66→2.88(+22bp)」 |
| D12b-TIPS-levels-1023 | TIPS_10Y @2026-10-23 / @2026-11-19 | [2.66, 2.88] | [2.66, 2.88] | 一致 |  |
| E1-SPX-chg | SPX 2026-10-23→2026-11-23 (7623.680176→7203.850098) | -5.5069 | -5.51 | 一致 |  |
| E1-SPX-ends | series_store.SPX @2026-10-23 / @2026-11-23 | [7623.680176, 7203.850098] | [7623.68, 7203.85] | 一致 |  |
| E2-NIKKEI225-chg | NIKKEI225 2026-10-23→2026-11-20 (62693.16→56436.65) | -9.9796 | -9.98 | 一致 |  |
| E2-NIKKEI225-ends | series_store.NIKKEI225 @2026-10-23 / @2026-11-20 | [62693.16, 56436.65] | [62693.2, 56436.65] | 一致 | MAP 表起值显示 1 位小数(62693.2),序列值 62693.16→按显示精度比对(席位首版按 2 位比对有误,已更正) |
| E3-GOLD_F-chg | GOLD_F 2026-10-23→2026-11-23 (4007.899902→3685.199951) | -8.0516 | -8.05 | 一致 |  |
| E3-GOLD_F-ends | series_store.GOLD_F @2026-10-23 / @2026-11-23 | [4007.899902, 3685.199951] | [4007.9, 3685.2] | 一致 | MAP 表起值显示 1 位小数(62693.2),序列值 62693.16→按显示精度比对(席位首版按 2 位比对有误,已更正) |
| E4-DXY-chg | DXY 2026-10-23→2026-11-23 (101.809998→104.079002) | 2.2287 | 2.23 | 一致 |  |
| E4-DXY-ends | series_store.DXY @2026-10-23 / @2026-11-23 | [101.809998, 104.079002] | [101.81, 104.079] | 一致 |  |
| E5-VIX-chg | VIX 2026-10-23→2026-11-23 (19.450001→27.01) | 38.8689 | 38.87 | 一致 |  |
| E5-VIX-ends | series_store.VIX @2026-10-23 / @2026-11-23 | [19.450001, 27.01] | [19.45, 27.01] | 一致 |  |
| E7-SPX-close-basis | SPX 2026-11-20 / 2026-10-23 (7623.680176→6910.390137) | -9.3562 | -9.36 | 一致 | 同日收盘口径 |
| E8-VIX-close-basis | VIX 2026-11-20 / 2026-10-23 (19.450001→35.889999) | 84.5244 | 84.52 | 一致 | 同日收盘口径 |
| E9-SPX-3m-close | SPX 2026-11-20 / 2026-08-19 (7707.97998→6910.390137) | -10.3476 | -10.35 | 一致 | 三个月收盘口径 |
| E10-VIX-3m-close | VIX 2026-11-20 / 2026-08-19 (14.89→35.889999) | 141.0342 | 141.03 | 一致 |  |
| E10b-VIX-3m-ends | VIX @2026-08-19 / @2026-11-20 | [14.89, 35.889999] | [14.89, 35.89] | 一致 |  |
| E11-UST-asset-row | UST_10Y 2026-11-19 / 2026-10-23 (5.0→5.04) | 0.8 | 0.8 | 一致 | MAP 资产月窗行 +0.8% |

### ⑥ 转折判断与候选面(9 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| B36-EAHICP-year-high | EA_HICP_YOY 2026 年内最大值 | {"max": 4.0, "at": ["2026-10-01"]} | {"max": 4.0, "at": ["2026-10-01"]} | 一致 | 「读数为年内新高」 |
| B48-JPR-2026-upsteps | JP_POLICY_RATE 2026 年内月均上行台阶 | [["2026-01", 0.728], ["2026-06", 0.841], ["2026-07", 0.978], ["2026-09", 1.043], ["2026-10", 1.227]] | 2026-01,06,07 (+09,10) | 一致 | 「2026-07 为 2026 年内第三个上行月均台阶(此前 2026-01 +17bp、2026-06 +11bp)」 |
| F1-CPI-delta | CPI 同比 2026-05 − 2026-02 | 1.7326 | 1.7326 | 一致 | 「三个月上行 1.7326 个百分点」 |
| F2-CPI-yoy-2026-max | CPI 同比 2026 年内最大值 | {"max": 4.1666, "at": ["2026-05"]} | {"max": 4.1666, "at": ["2026-05"]} | 一致 | 「2026-05 高点 4.17」 |
| F7-pool-max | report.research_plan.turning_candidates.candidates \|Δ\| 最大者 | {"metric": "CPI", "delta": 1.7326, "n_pool": 7} | {"metric": "CPI", "delta": 1.7326, "n_pool": 7} | 一致 |  |
| F7b-pool-recompute | 候选池 7 项前值→后值 series_store 复算 | [true, true, true, true, true, true, true] | 7/7 一致 | 一致 |  |
| F8-rank-2026-09 | EA_HICP_YOY@2026-09 vs CPI 同比 2026-09 | {"EA": 3.8, "US": 3.7173} | EA > US | 一致 |  |
| F8b-rank-crossings | EA_HICP_YOY vs CPI 同比 全史可比月份位次 (series_store 直算) | {"n_comparable": 106, "first": "2017-11", "months_EA_gt_US_earlier_than_2026-09": 15, "earlier_crossing_span": ["2022-07", "2023-09"], "consecutive_EA_lt_US_right_before_2026-09": 34, "2026_rank": ["EA<US", "EA<US", "EA<US", "EA<US", "EA<US", "EA<US", "EA<US", "EA<US", "EA>US"]} | 「两地最新可比同月为九月,更早月份位次有交叉」 | 一致 | 字面属实: 2022-07..2023-09 共 15 个月 EA>US;但其后 2023-10..2026-08 连续 34 个可比月均 EA<US,2026-09 为 2023-09 以来首次反超——陈述未给时间范围(见 MINOR) |
| F8c-ea-path-2026 | EA_HICP_YOY 2026 逐月 | [["2026-01", 1.7], ["2026-02", 1.9], ["2026-03", 2.6], ["2026-04", 3.0], ["2026-05", 3.2], ["2026-06", 2.8], ["2026-07", 2.9], ["2026-08", 3.2], ["2026-09", 3.8], ["2026-10", 4.0]] | 见 note | 一致 | 2026-01=1.7; 2026-02=1.9; 2026-03=2.6; 2026-04=3.0; 2026-05=3.2; 2026-06=2.8; 2026-07=2.9; 2026-08=3.2; 2026-09=3.8; 2026-10=4.0 |

### ⑦ 传导链各环(1 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| I5-USDJPY-12m-position | USDJPY [2025-11-23..2026-11-23] 末值/窗内最小/最大/末值分位 | {"last": ["2026-11-23", 159.347], "min": 152.453, "max": 163.864, "pct_rank": 71.0, "n": 259, "m1_pct": 1.82, "m3_pct": -0.13} | {"last": "2026-11-23=159.347", "min": 152.453, "max": 163.864, "pct_rank": 71.0, "n": 259, "m1_pct": 1.82, "m3_pct": -0.13} | 一致 | 「USDJPY 仍处高位」: 12 个月窗内约 71% 分位(窗内最大 163.864),近一月 +1.82%、三个月 -0.13% |

### ⑧ 历史类比(零段)(2 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| L1-analog-top-face | report.steps[S6_analog].envelope.data.top | [[1, "2025-03", 0.727212], [2, "2022-06", 0.791806], [3, "2023-10", 1.054168], [4, "2021-02", 1.284945], [5, "2020-01", 1.357685]] | FULL_REPORT「历史相似结构」5 段 | 一致 | 引擎候选面 5 段(候选月全窗数据事后筛得) |
| L2-history-zero-case | agent_judgment.reader_map.history_periods / history_zero_case_note; report.agent_judgment.reader_map_faces.history_n | {"history_periods": [], "history_n": 0, "note_len": 159} | {"history_periods": [], "history_n": 0, "note": "在场"} | 一致 | 零段类比: 引擎候选 5 段在场,判断档未采纳任何段、未引任何候选数字(无可复算数字);事后结果≠当时可知的表述与引擎注记一致 |

### ⑨ 情景(8 点,偏离 1)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| J0-hicp-release-schedule | EA_HICP_YOY 观测月→规则发布日(月末+16,引擎同规则) | {"2026-09": "2026-10-16", "2026-10": "2026-11-16", "2026-11": "2026-12-16", "2026-12": "2027-01-16", "2027-01": "2027-02-16"} | {"2026-10": "2026-11-16", "2026-11": "2026-12-16", "2026-12": "2027-01-16", "2027-01": "2027-02-16"} | 一致 |  |
| J1-S1-trigger-not-met | 截止日读数: EA_HICP_YOY@2026-10 / CORE_PCE 同比@2026-09 / TIPS_10Y@2026-11-19 | {"EA": 4.0, "CORE_PCE_yoy": 3.12, "TIPS": 2.88} | {"EA": "<4.2", "CORE_PCE_yoy": "<3.2", "TIPS": "<3.0"} | 一致 | S1 触发条件在截止日尚未到达=待验证情景 |
| J2-S1-state-holds-at-cutoff | 同上三项读数 vs S1 情景状态(维持 3.5% 以上 / 3.0% 以上) | {"EA": 4.0, "CORE_PCE_yoy": 3.12} | {"EA": ">=3.5", "CORE_PCE_yoy": ">=3.0"} | 一致 | S1 前提与截止日读数相容(未被证伪) |
| J3-S2-trigger-not-met | 截止日读数: EA_HICP_YOY 2026-09→2026-10 / BEI_10Y@2026-11-20 | {"EA_09": 3.8, "EA_10": 4.0, "BEI": 2.15} | {"EA": "未连续回落", "BEI": ">2.0"} | 一致 | S2 触发条件尚未到达 |
| J4-S2-falsifier-reachable | S2 证伪: 2026-12 与 2027-01 两月发布=2026-11/2026-12 观测月(2026-12-16/2027-01-16),期限 2027-02-15 | {"releases": ["2026-12-16", "2027-01-16"], "<=deadline": true} | 两次发布均在期限内=可观测可触发 | 一致 |  |
| J5-S1-falsifier-reachable | S1 证伪字面「2027-01 前发布…连续两个月低于 3.0%」直算 | {"obs_months_released_before_2027-01": ["2026-09", "2026-10", "2026-11"], "release_dates": ["2026-10-16", "2026-11-16", "2026-12-16"], "consecutive_pairs(obs_month,reading)": [["2026-09", 3.8, "2026-10", 4.0], ["2026-10", 4.0, "2026-11", null]], "reachable": false} | 证伪条件可观测且与截止日读数相容(可触发) | **偏离** | 偏离: 截止日后、2027-01 前只剩 2026-11 观测月一次发布(2026-12-16);可与它相邻的 2026-10 读数=4.0 已于 2026-11-16 发布→「连续两个月低于 3.0%」在 2027-01 前不可能成立,S1 证伪条件按字面不可触发(见 MAJOR-1) |
| J6-scenarios-complementary | S1 状态(维持 3.5% 以上/3.0% 以上) vs S2 状态(回落至 3.0% 以下/2.8% 以下) | S1=延续上行, S2=回落;资产方向 S1=利率上/风险资产弱/美元强, S2=通胀补偿与实际利率回落/风险资产与黄金修复/美元弱 | 方向互补 | 一致 | 两情景方向互补非孤证;S1 证伪阈(<3.0)与 S2 证伪阈(>=4.0)互补 |
| J7-trigger-release-window | S1 触发「2026-12 或 2027-01 发布」对应发布日 | ["2026-12-16", "2027-01-16"] | 均 <= 2027-02-15 | 一致 | 2027-01 观测月发布日 2027-02-16 晚于期限→「至 2027-01」只能指发布月(2026-11/2026-12 观测月) |

### ⑩ 总判断 / 走位 / 对质表文字与数值(10 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| B11-INDPRO-level-chg | INDPRO 2026-10 / 2026-07 | 0.2209 | 0.22 | 一致 | 走位面「仅 +0.22%」 |
| B12-INDPRO-mom-10 | INDPRO 2026-10 / 2026-09 (103.3954 / 103.8458) | -0.4337 | -0.43 | 一致 | 「2026-10 环比 -0.43%」 |
| B13-INDPRO-base-2025 | INDPRO 2025-10 / 2025-07 (101.2195 / 101.894) | -0.662 | -0.66 | 一致 | 「上年 2025-07→2025-10 基数下行 0.66%」 |
| B32-EAHICP-delta | EA_HICP_YOY 2026-10 − 2026-07 | 1.1 | 1.1 | 一致 | 「三个月上行 1.1 个百分点」 |
| F9-headline>core | CPI 同比 2026-09 vs CORE_CPI 同比 2026-09 | [3.7173, 2.5658] | headline 3.72 > core 2.57 | 一致 |  |
| F10-magnitude-EA-vs-US | HICP 同比 Δ(07→10) vs CPI 同比 Δ(07→09 最近有效) | [1.1, 0.41] | 欧元区幅度更大 | 一致 |  |
| K7-MAP-asset-row-SHCOMP | SHCOMP 2026-10-23→2026-11-23 (3690.4753→3538.948) | [-4.1059, 3690.4753, 3538.948] | [-4.11, 3690.48, 3538.95] | 一致 | MAP 资产月窗表引擎行(判断档未引用) |
| K7-MAP-asset-row-DAX | DAX 2026-10-23→2026-11-23 (25181.650391→25209.449219) | [0.1104, 25181.650391, 25209.449219] | [0.11, 25181.7, 25209.4] | 一致 | MAP 资产月窗表引擎行(判断档未引用) |
| M3-unrendered-fields | MAP_REPORT.md 是否含 verdict_note / narrative 专有句 | {"verdict_note": [false, false, false], "narrative": [false, false, false]} | 均不进渲染(与 quality_gate_notes 一致) | 一致 |  |
| M4-reader-map-verbatim | MAP_REPORT.md 含判断档 headline/走位/传导/转折/情景证伪与触发原文 | 17/17 | 全部逐字渲染 | 一致 | 读者报告判断文字=判断档原文(含 S1 证伪句) |

### ⑪ 诚实缺席项(15 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| G1-gate-a-status | snapshot.gate_a.status | DEGRADED | DEGRADED | 一致 |  |
| G1b-core-missing | snapshot.gate_a.core_missing | [] | [] | 一致 |  |
| G1c-noncore-missing | snapshot.gate_a.noncore_missing | ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"] | ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"] | 一致 |  |
| G1d-noncore-degraded | snapshot.gate_a.noncore_degraded | ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"] | ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"] | 一致 |  |
| G2-EAGDP-age | series_store.EA_REAL_GDP_YOY 末观测距截止日天数 / 注册表 max_calendar_lag_days | [145, 120, 1.208] | [145, 120, 1.208] | 一致 | 「145 天,超过 120 天;与 US_REAL_GDP 同龄同倍数」 |
| G2b-EAGDP-has-stock | series_store.EA_REAL_GDP_YOY 观测数 | 123 | >0(存量观测在库) | 一致 | 列入非核心缺口清单但库内有存量观测——判断档已披露 |
| G3-USGDP-age | US_REAL_GDP 末观测距截止日天数 / 注册表上限 / 倍数 | [145, 120, 1.208] | [145, 120, 1.208] | 一致 | 「1.2 倍」 |
| G4-CPCE-age | CORE_PCE 末观测距截止日天数 / 注册表上限 / 倍数 | [83, 60, 1.383] | [83, 60, 1.383] | 一致 | 「83 天,为 60 天的 1.4 倍」 |
| G5-task-window-empty | report.run.data_requirements.items[*].spec.window.n_in_window | {"US_REAL_GDP": 0, "UNEMPLOYMENT": 0, "INDPRO": 0, "CPI": 0, "CORE_CPI": 0, "CORE_PCE": 0, "EA_REAL_GDP_YOY": 0, "EA_HICP_YOY": 0, "JP_POLICY_RATE": 0} | 9 项均为 0 | 一致 |  |
| G5b-outcomes | report.run.data_requirements.items[*].outcome | ["insufficient_coverage"] | ["insufficient_coverage"] | 一致 |  |
| G6-ref-count | agent_judgment.l3/l4 evidence_refs 计数 | {"C": 10, "M": 4, "S": 5, "total": 19} | {"C": 10, "M": 4, "S": 5, "total": 19} | 一致 |  |
| G6b-refs-resolve | evidence_refs ∩ report.evidence_index | [] | 全部解析 | 一致 | 证据索引键样例: ['AAPL@2026-11-23', 'BB_OAS@2026-11-19'] |
| G8-facts-count | report.run.evidence_gate.counts | {"facts_kept": 105, "facts_rebuilt": 0, "facts_dropped": 0, "facts_excluded_version": 0, "series_observations_dropped": 0} | {"facts_kept": 105, "facts_rebuilt": 0, "facts_dropped": 0, "facts_excluded_version": 0, "series_observations_dropped": 0} | 一致 |  |
| G8b-facts-len | snapshot.facts 长度 | 105 | 105 | 一致 |  |
| I1-evidence-index-rows | report.evidence_index 长度 | 63 | 63 | 一致 | agent_declaration「证据索引(63行)」/FULL_REPORT「证据行: 63」 |

### ⑫ 截止日当日标注(2 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| M1-intraday-label | agent_judgment 全文「盘中快照」出现次数 / 报告内 2026-11-23 日频值(SPX/VIX/GOLD_F/DXY/USDJPY) | {"n_label": 5, "as_of": "2026-11-23T22:53:47+08:00"} | {"n_label": ">=4", "as_of": "2026-11-23T22:53:47+08:00"} | 一致 | 截止日当日值均带「盘中快照、非收盘价」说明;与 research_as_of(纽约 09:53)相容 |
| M5-map-cutoff-header | MAP_REPORT.md 研究截止日行 | true | true | 一致 |  |

### ⑬ 契约非 VERIFIED 项(4 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| H1-stale-items | report.agent_judgment.contract_verification.verdicts status!=VERIFIED | [["CORE_PCE", "130.902", "STALE", "recompute:Fact 直读 CORE_PCE@2026-09-01=130.902"], ["US_REAL_GDP", "24611.077", "STALE", "recompute:Fact 直读 US_REAL_GDP@2026-07-01=24611.077"]] | CORE_PCE 与 US_REAL_GDP 两项 STALE | 一致 |  |
| H2-stale-values-equal | contract_verification STALE 项 value==expected | true | true | 一致 | 「数值一致、观测滞后超过注册表节奏」 |
| H3-stale-disclosure | agent_judgment.quality_gate_notes[3] | true | true | 一致 | STALE 指标/观测期/滞后天数披露 |
| H4-contract-stats | contract_verification.stats | {"checks": 9, "contradicted": 0, "verified": 7, "unbound": 0, "six_fail": 0, "map_fail": 0, "n_contradictions": 3} | {"checks": 9, "verified": 7, "contradicted": 0} | 一致 |  |

### ⑭ 交付门相关披露(4 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| C9-target-series-absent | metric_registry.metrics[*].metric_id + snapshot.series_store keys | {"in_registry": false, "in_store": false} | {"in_registry": false, "in_store": false} | 一致 |  |
| K1-plan-has-no-US-EA-policy-rate | report.run.data_requirements.items[*].metric_id | ["CORE_CPI", "CORE_PCE", "CPI", "EA_HICP_YOY", "EA_REAL_GDP_YOY", "INDPRO", "JP_POLICY_RATE", "UNEMPLOYMENT", "US_REAL_GDP"] | 不含美欧政策利率序列 | 一致 | 「本问计划指标面未纳入美欧政策利率序列」属实 |
| K2-store-has-US-EA-policy-rates | series_store DFEDTARU/DFEDTARL/ECB_DFR/ECB_MRO/FED_FUNDS [2026-08-19..2026-11-23] 变更点 | {"DFEDTARU": [["2026-09-17", 3.75, 4.0]], "DFEDTARL": [["2026-09-17", 3.5, 3.75]], "DFF": [["2026-09-17", 3.63, 3.88]], "FED_FUNDS": [["2026-09-01", 3.63, 3.75], ["2026-10-01", 3.75, 3.88]], "ECB_DFR": [["2026-09-16", 2.25, 2.5]], "ECB_MRO": [["2026-09-16", 2.4, 2.65]]} | 判断档未引用(称「依本问证据不可判」) | 一致 | 快照在库但不在本问计划指标面/证据索引: 美联储目标区间上限 2026-09-17 起 3.75→4.00(+25bp),欧央行存款便利利率 2026-09-16 起 2.25→2.50(+25bp)——与日本央行 2026-09-18 决议同月收紧;计划面/证据索引确未纳入(披露口径见 MINOR) |
| K3-JGB-registered-not-collected | metric_registry JGB2Y/5Y/10Y 在册; series_store 是否在库 | {"registered": true, "in_store": []} | {"registered": true, "in_store": []} | 一致 | 「本引擎无日本融资成本/套息持仓序列」: 套息持仓序列确无;JGB 收益率在册但本轮未采,JP_POLICY_RATE 本身即隔夜资金利率月均(措辞见 NIT) |

### 第 4 节 六查在场对照(竞争解释 / 反对证据)(4 点,偏离 0)

| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |
|---|---|---|---|---|---|
| I6-BEI-earlier-leg-endpoints | BEI_10Y [2026-02-20..2026-05-04] 窗内最小/最大;月末对照 2026-02-27→2026-05-29 | {"window_min": ["2026-02-27", 2.25], "window_max": ["2026-05-04", 2.5], "month_end_05-29": 2.38, "me_to_me_bp": 13.0} | {"window_min": "2026-02-27=2.25", "window_max": "2026-05-04=2.5", "month_end_05-29": 2.38, "me_to_me_bp": 13} | 一致 | 判断档两端点=该窗最小值→最大值(05-04 亦为 2026 年内最高);月末对月末仅 +13bp——端点未注明「段内峰值」(见 MINOR) |
| K4-UMCSENT-anchor-window | UMCSENT @2026-07-01 / @2026-10-01 | [55.2, 48.0] | [55.2, 48.0] | 一致 | 判断档未引用的软数据(不在本问计划指标面与证据索引,仅快照在库): 锚窗内回落 7.2 点(见六查 C2) |
| K5-EURUSD-3m | EURUSD 2026-11-23 / 2026-08-19 | -5.52 | -5.52 | 一致 | 「弱欧元放大输入压力」前提: 三个月 -5.52%、近一月 -2.51%,同向 |
| K6-BRENT-windows | BRENT_F 近一月/三个月/12 个月 | [-24.44, -3.74, 38.86] | [-24.44, -3.74, 38.86] | 一致 | 能源前提的在场对照: 近一月 -24.44%,判断档未引用(见六查 C1) |

## 3. 分类核对要点(数字出处见第 2 节对应点)

① 截止日: 报告、快照 target_date、research_as_of 三处一致(2026-11-23;2026-11-23T22:53:47+08:00);判断档所载截止时点各城市钟(纽约 09:53、法兰克福 15:53、东京 23:53、上海 22:53)由 +08:00 换算一致;series_store 无晚于截止日的观测(计数 0);9 个锚格的发布日均不晚于各锚 as_of——其中 CORE_PCE「3 个月前」取 2026-06 观测是正确的(2026-07 观测在库值 130.148,但规则发布日 2026-08-30 晚于锚 as_of 2026-08-23)。

② 点值锚: 9 格 18 锚全部一致——US_REAL_GDP 24408.011→24611.077;UNEMPLOYMENT 4.1→4.1;INDPRO 103.1675→103.3954;CPI 332.813→337.476;CORE_CPI 336.789→339.9;CORE_PCE 129.969→130.902;EA_REAL_GDP_YOY 1.19→1.28;EA_HICP_YOY 2.9→4.0;JP_POLICY_RATE 0.978→1.227;判断档 anchor_echo 18/18 与引擎格一致;USDJPY 159.35@2026-11-23 一致。

③ 同比: 全部为去年同月 / 同季基期——GDP 2.19% / 2.07%(基期 2025-04 / 2025-07 同季);INDPRO 1.25% / 2.15%(基期 2025-07 / 2025-10);CPI 3.3%(基期 2025-07);核心 CPI 2.47%(基期 2025-07);CORE_PCE 3.04% / 3.12%(基期 2025-06 / 2025-09);CPI 与核心 CPI 2026-10 因缺 2025-10 基期如实标「不可得」,最近有效同比=2026-09(3.7173 / 2.5658);转折与候选面所引同比(2026-02 / 05 / 08 / 09 及 2025-11 / 2026-02)直算一致。

④ 政策面: 冻结日历 RC-JP-BOJ-TARGET-2026-09: decision_date 2026-09-18 / effective_on 2026-09-24 / target_value 1.25;RC-JP-BOJ-MAINT-2026-10: 2026-10-30、target 1.25、无 effective_on 键;距上次调整 2026-11-23−09-24=60 天、−09-18=66 天,距维持 24 天;官方目标 / 市场月均 / 决议日 / 生效日四者分列,无互相冒充;JP_POLICY_TARGET 不在注册表也不在 series_store(披露属实);JP_POLICY_RATE 注册名=「日本无担保隔夜拆借利率(月均)」;生效后首个整月=2026-10;政策一年窗净变动 +67bp(2026-10−2025-12=67.0)与 +75bp(−2025-11=74.9)两口径并列且均成立;政策事件簇为空、政策文档事实仅 FOMC-MINUTES-2026-10(2026-11-18 发布,不晚于截止日),与报告一致。

⑤ 三利率分解与资产月窗: 三窗恒等式残差 0(近一月 −8=+11−19;三个月 +39=+53−14;12 个月 +91=+102−11);期末水平名义 5.04 / 实际 2.88(2026-11-19)、盈亏平衡 2.15(2026-11-20,12 个月窗内最低,n=252);BEI_10Y 早段端点 2.25@2026-02-27、2.50@2026-05-04;引擎「近 30 日」窗(2026-10-23→2026-11-20)−19bp;资产窗 SPX −5.51%、NIKKEI225 −9.98%、GOLD_F −8.05%、DXY +2.23%、VIX +38.87%(19.45→27.01)、UST_10Y 5→5.04;收盘口径 SPX −9.36% / VIX +84.52%;三个月收盘口径 −10.35% / +141.03%(14.89→35.89);读者报告引擎行 SHCOMP −4.11%、DAX +0.11% 逐位一致。

⑥ 转折与候选面: 候选池 7 项前值→后值 7/7 直算一致;最大 |Δ|=CPI 2026-02→2026-05 +1.7326;EA_HICP 1.9→3.2;JP_POLICY_RATE 2026-04 0.727→2026-07 0.978;2026 年内月均上行台阶 01 / 06 / 07 / 09 / 10 月(+17 / +11 / +14 / +7 / +18bp),「第三个上行台阶」计数一致;「同月先后未定」的月频分辨率声明与候选面一致;EA_HICP 2026-10=4.0 为年内最高;CPI 同比年内最高 4.1666@2026-05;2026 年 1–8 月各月 EA 均低于美国,9 月为 2023-09 以来首个高于美国的可比月。

⑦ 传导链: M1 三环分级 E1 / E2 / E2 与证据相称——环 1 全部数字可回贴;环 2 明写「【假设】」并附缺环注记;环 3 观察数字(USDJPY 159.35、NIKKEI225 −9.98%)可回贴。

⑧ 历史类比: 零段呈现;引擎候选面 5 段(2025-03 / 2022-06 / 2023-10 / 2021-02 / 2020-01)在场,判断档未采纳任何段、未引任何候选数字;「事后结果≠当时可知」的表述与引擎注记一致,无事后冒充。

⑨ 情景: S1 / S2 触发条件在截止日均未到达(S1:EA 4.0<4.2、CORE_PCE 3.12<3.2、TIPS_10Y 2.88<3.0;S2:EA 3.8→4.0 未回落、BEI_10Y 2.15>2.0);S1 状态与截止日读数相容(EA 4.0≥3.5、CORE_PCE 3.12≥3.0);两情景方向互补;S2 证伪(2026-12 与 2027-01 两月发布)的两次发布日 2026-12-16 / 2027-01-16 均在期限 2027-02-15 内,可观测可触发;**S1 证伪按字面不可触发(唯一偏离,见 MAJOR-1)**。

⑩ 文字与数值: headline 3.7173>core 2.5658;「欧元区幅度更大」=1.1 对 0.41 个百分点;INDPRO 水平 +0.22%、环比 −0.43%、基数 −0.66%;对质表「尚不能区分 / 尚不能区分 / 支持主解释」与各行观测一致(见第 4 节 4.5);读者报告对判断档原文逐字渲染 17/17(含 S1 证伪句);verdict_note 与 narrative 不进渲染的声明属实。

⑪ 诚实缺席: Gate A=DEGRADED、核心缺口 0、非核心缺口 7 项与非核心降级 8 项逐项一致;EA_REAL_GDP_YOY 末观测距截止日 145 天 / 上限 120 天=1.208 倍、US_REAL_GDP 同为 145 / 120、CORE_PCE 83 / 60=1.383 倍(「1.4 倍」);任务窗口 9 指标 n=0、outcome=insufficient_coverage;证据引用 10+4+5=19 条全部解析到证据索引;facts 105。

⑫ 截止日当日标注: 判断档 5 处「盘中快照」标注,覆盖 SPX / VIX / GOLD_F / DXY / USDJPY 的 11-23 值;与 research_as_of(纽约 09:53)相容;读者报告截止日行一致。

⑬ 契约非 VERIFIED 项: 两项 STALE(CORE_PCE 130.902@2026-09-01、US_REAL_GDP 24611.077@2026-07-01)在判断档数据面按指标 / 观测期 / 滞后天数 / 倍数披露,与引擎面一致;契约 stats: checks=9、verified=7、contradicted=0。

⑭ 交付门相关披露: JP_POLICY_TARGET 缺数格、政策事件簇为空、「本问计划指标面未纳入美欧政策利率序列」(计划 9 指标确无美欧政策利率)均属实;无「缺席写成无变化」,无「序列值写成官方宣布目标」。

## 4. 六查逐项结论与反方攻击记录

### 4.1 C1-INFL-SYNC(美欧通胀同步走高、欧元区幅度更大)

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 相符 | 所引 EA_HICP_YOY@2026-10-01、CPI / CORE_CPI@2026-10-01、CORE_PCE@2026-09-01、BEI_10Y@2026-11-20 均为通胀或通胀定价指标,且全部在证据索引内 |
| 支持度 | 相称 | EA 2.9→4.0(+1.1);美国 CPI 同比 3.3039→3.7173、核心 2.4665→2.5658、CORE_PCE 3.0412→3.1212,三口径同向;「幅度更大」=1.1 对 0.41 |
| 竞争解释 | 在列且真正竞争 | 成本持续传导 vs 低基数 / 一次性扰动,两条均标【假设】,同一证据可容纳,非稻草人 |
| 反对证据 | 有一处在场未引(MINOR-4) | 证据索引在列 BRENT_F@2026-11-23=88.19;快照直算近一月 116.72→88.19=−24.44%、三个月 91.62→88.19=−3.74%、12 个月 +38.86%——三个月窗内油价微降而两地通胀走高,对「能源持续传导」前提是反向事实、对「能源基数」消退假设是同向事实;「弱欧元」前提与 EURUSD 三个月 −5.52% 同向 |
| 结论是否超出证据 | 否 | 「水平高于美国」限定在「最新可比同月」(2026-09:3.8 对 3.7173),并注明 2026-10 美国同比不可比 |
| 证伪可观测性 | 由 S1 / S2 承担 | C1 未自设证伪条款;区分指标 BEI_10Y 在场 |

反方攻击记录:
1. 攻击「同步走高」: 美国端只到 9 月,且 3.72 低于 2026-05 高点 4.17,能否称走高?→ 成立: 3 个月前锚 2026-07=3.3039,最近有效 2026-09=3.7173,方向为升;10 月缺基期已在句内披露,未以相邻月替代(若替代会得 3.82%)。
2. 攻击「水平高于美国」: 差距仅约 0.08 个百分点,是否在舍入内翻转?→ 不翻转: EA 3.8 为一位小数,真值不小于 3.75,大于 3.7173。
3. 攻击「更早月份位次有交叉」: 是否夸大交叉频率?→ 字面属实但缺时间范围: 全史 106 个可比月(2017-11 起)中 EA 高于美国的只有 2022-07 至 2023-09(15 个月)与 2026-09,其前 34 个可比月(2023-10 至 2026-08)均为 EA 低于美国 → 记 MINOR-1。
4. 攻击传导环 1「尚不能区分」是否偏保守 → 三窗 BEI_10Y 方向一致向下(−14 / −19 / −11bp)合竞争解释,但「通胀读数数月内自行回落」一半未兑现(EA 2026-10=4.0 为年内新高);早段 2.25→2.50 的两个端点是窗内最小值→最大值(2026-05-04 亦为 2026 年内最高;月末对月末 2026-02-27→2026-05-29 仅 +13bp 至 2.38),端点未标注 → 记 MINOR-2;裁定方向不变。

### 4.2 C2-GROWTH-STABLE(两地增长面大体平稳)

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 相符 | GDP 水平、失业率、工业生产均为增长硬数据 |
| 支持度 | 相称 | GDP 同比 2.19→2.07;失业率 4.1→4.1(窗内 4.1 / 4.1 / 4.2 / 4.1);INDPRO 水平 +0.22%;EA GDP 同比 1.19→1.28 |
| 竞争解释 | 在列且真正竞争 | 制造业回暖 vs 基数效应,均标【假设】 |
| 反对证据 | 证据面内无;证据面外见 NIT-8 | 快照库内 UMCSENT 55.2(2026-07)→48.0(2026-10),但该序列不在本问计划指标面与证据索引 |
| 结论是否超出证据 | 否 | 「未见方向性转折」有两锚数值支撑;工业同比回升被如实写入并解释为含基数效应(环比 −0.43%、基数 −0.66%) |
| 证伪可观测性 | 可由后续 INDPRO 同比 / 失业率读数观测 | 未单设条款 |

反方攻击记录:
1. 攻击「平稳」: 工业同比 1.25→2.15(约 +0.90 个百分点)、失业率处于低位,增长动能是否已重新加速?→ 指数水平仅 +0.22%,2026-10 环比 −0.43%,同比抬升主要来自基数(2025-07→2025-10 下行 0.66%),GDP 同比小幅回落;判断档已把「重新加速」列为竞争【假设】而非结论 → 陈述成立。
2. 攻击 EA GDP 同比 +0.09 是否构成「上行」→ 幅度微小且两锚相隔一个季度,判断档写「仅微幅变动」→ 相称。

### 4.3 C3-JP-POLICY(日本政策利率抬升通道)

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 相符 | 冻结日历两条日本央行实录 + JP_POLICY_RATE 月均 + USDJPY |
| 支持度 | 相称 | 目标 1.25 / 决议 2026-09-18 / 生效 2026-09-24 / 维持 2026-10-30 逐项一致;60 / 66 天直算一致;+67bp / +75bp 两口径均成立(67.0 / 74.9) |
| 竞争解释 | 在列且真正竞争 | 连续上调 vs 决议跨月均值效应;后者带入 2026-09 月均仅 +7bp(决议 09-18、生效 09-24 落在 9 月最后一周)的事实 |
| 反对证据 | 无未披露的反向事实 | 「次月月均尚未发布」「此后是否有新决议引擎日历无条目」如实 |
| 结论是否超出证据 | 否 | 月均 0.478→1.227 的台阶路径与官方记录相容 |
| 证伪可观测性 | 可观测 | 「下月月均应维持当前水平附近」可由 JP_POLICY_RATE 2026-11 月均检验 |

反方攻击记录:
1. 攻击「距上次调整 60 / 66 天」: 可否被读成自 2026-10-30 维持会议起算(24 天)?→ 句内明确「上次调整」有决议日 / 生效日两种起算,与日历条目注记「距上次调整按生效日计算」一致;维持会议另行披露 → 成立。
2. 攻击「官方与市场相互印证」: 月均 1.227% 低于目标 1.25%,印证是否成立?→ 1.227 是 10 月整月均值,目标 09-24 生效,月均略低于目标符合均值口径;判断档明确该序列「非政策目标宣布值」→ 成立。

### 4.4 M1-JP-RATE-PATH(机制链)

| 环 | 证据级 | 结论 |
|---|---|---|
| 环 1 政策利率路径 | E1 | 相称;0.478 / 0.557 / 0.728 / 0.841 / 0.978 / 1.043 / 1.227 与 +67 / +75bp 全部可回贴 |
| 环 2 融资成本→套息压缩 | E2 | 明写「传导【假设】」并附缺环注记;套息持仓序列确不在库;措辞「无日本融资成本序列」略过宽(NIT-1) |
| 环 3 资产面对照 | E2 | 观察数字一致(USDJPY 159.35;NIKKEI225 −9.98%);「利差仍高」以事实位措辞出现而本问证据无利差序列(MINOR-3) |

反方攻击记录:
1. 攻击环 3: 若加息传导成立,USDJPY 应走低,实际如何?→ USDJPY 近一月 156.494→159.347(+1.82%)、三个月 −0.13%、12 个月窗(2025-11-23 至 2026-11-23,n=259)内约 71% 分位(窗内最大 163.864)→ 未走低;环 3 已如实写「USDJPY 仍处高位…传导方向证据不单一」→ 未超出证据。
2. 攻击环 3: 「股指已明显回落」是否被归因于加息?→ 环 3 未作单一归因(标混合态,区分指标=USDJPY,并注明多因子驱动)→ 相称。

### 4.5 CH-INFL-RATES-RISKOFF(reader_map 传导链)

| 环 | 对质裁定 | 席位结论 |
|---|---|---|
| 环 1 区分指标 BEI_10Y | 尚不能区分 | 与观测一致: 三窗 −14 / −19 / −11bp 合竞争解释「走低或持平」,EA 读数未回落使其另一半未兑现,早段 2.25→2.50 合主解释;端点选择见 MINOR-2 |
| 环 2 区分指标 TIPS_10Y | 尚不能区分 | 与观测一致: 三窗恒等式残差 0;两解释在该指标上预言同向且文中已自陈「不分立」;主解释前件(央行紧缩偏向)未举证已写入 verdict_note(该字段不进读者报告渲染,但 observed_fact 已载「两解释…预期方向不分立」这一裁定理由) |
| 环 3 TIPS_10Y 对 SPX | 支持主解释 | 与观测一致: TIPS_10Y +22bp(2026-10-23→2026-11-19)与 SPX −5.51%(→2026-11-23)同现;两侧预期在区分指标上分立 |

反方攻击记录:
1. 攻击环 3 的窗口错配: TIPS_10Y 止于 11-19 而 SPX 取 11-23,方向是否会变?→ 以共同窗 2026-10-23→2026-11-19 复算 SPX −5.87%,方向不变;错配已在文中披露(NIT-3)。
2. 攻击链级一致性: 环 1、2 判「尚不能区分」而环 3 判「支持主解释」,是否自相矛盾?→ 不矛盾: 环 3 两侧预期(TIPS_10Y 上行 vs 走低)分立且有在场观测;环 1、2 的两侧预期分立性弱或不可分;披露块「支持 ×1 / 尚不能区分 ×2」与逐环一致。
3. 攻击环 3 是否忽略流动性因素 → 文中已写「VIX 的涨幅幅度提示流动性/仓位因素可能叠加,单月窗不能完全区分」→ 未超出证据。

### 4.6 情景(S1-INFL-STICKY / S2-INFL-FADE)

| 查项 | S1 | S2 |
|---|---|---|
| 截止日是否已触发 | 否(EA 4.0<4.2;CORE_PCE 3.12<3.2;TIPS_10Y 2.88<3.0) | 否(EA 3.8→4.0 未回落;BEI_10Y 2.15>2.0) |
| 前提是否与截止日读数相容 | 是(EA 4.0≥3.5;CORE_PCE 3.12≥3.0) | 是(尚未回落,属待验证的反例情景) |
| 触发条件可观测性 | 可观测: 两次发布日均不晚于期限 2027-02-15 | 可观测 |
| 证伪条件可观测性 | **按字面不可触发(MAJOR-1)** | 可触发: 2026-12-16 / 2027-01-16 两次发布均在期限内 |
| 方向互补 | 延续上行 vs 回落;资产方向相反 | 同左 |

反方攻击记录:
1. 攻击「触发条件是否已被触发、前提是否与截止日读数相容、两情景是否孤证」→ 均未触发(S1: EA_HICP_YOY 4.0<4.2、CORE_PCE 3.12<3.2、TIPS_10Y 2.88<3.0;S2: EA_HICP_YOY 3.8→4.0 未回落、BEI_10Y 2.15>2.0),无「已触发的触发条件」被当作待验证;S1 前提与截止日读数相容,S2 属待验证的反例情景,两者方向互补(延续上行 vs 回落,资产方向相反),非孤证 → 通过。
2. 攻击「证伪条件是否可观测、期限是否与截止日读数相容」→ S2 可触发(2026-12-16 / 2027-01-16 两次发布均在期限 2027-02-15 内);S1 按字面不可触发 → MAJOR-1。

## 5. 问题清单

### MAJOR(1 条)

**MAJOR-1 证伪条件按字面不可触发(规程第 3 节⑨「期限与截止日读数相容」、第 5 节「证伪条件不可观测」)**

- 位置: `agent_judgment.json` → `l4.scenarios[id=S1-INFL-STICKY].rows.falsification.threshold`;逐字渲染于 `MAP_REPORT.md` 第 146 行、`FULL_REPORT.md` 第 81 行、`report.md` 第 90 行。
- 原句: 「若 2027-01 前发布的 EA_HICP_YOY 同比连续两个月低于 3.0%,通胀粘性假设被证伪」
- 直算(出处: `MAP_REPORT.md` 第 181 行发布日期列;`scripts/research_map_planner.py` 的 `RELEASE_RULES['EA_HICP_YOY']`=(monthly, 16, 月末+16 天推定);快照 series_store.EA_HICP_YOY):
  - 观测月→发布日: 2026-10→2026-11-16;2026-11→2026-12-16;2026-12→2027-01-16;2027-01→2027-02-16。
  - 「2027-01 前发布」且晚于截止日 2026-11-23 的只有 2026-11 观测月一次发布(2026-12-16)。
  - 要「连续两个月低于 3.0%」,唯一含未发布读数的相邻对是(2026-10,2026-11): 2026-10 读数=4.0,已于 2026-11-16 发布,不低于 3.0 → 该条件在截止日已确定不可能成立。
  - 冻结日历无欧元区 HICP 未来期次条目(仅 2021-05 / 2022-06 / 2025-03 三条历史实录,快报日分别为 2021-06-01 / 2022-07-01 / 2025-04-01,即次月 1 日);按该实录模式,2026-12 观测月的快报也落在 2027-01-01,不在「2027-01 前」——与规则推定日的结论相同(此为日历自有记录的模式,仅作旁证,主依据为上两条)。
- 为何是 MAJOR 而非行文问题: 证伪条款是情景「不对称结果须如实更新判断」的依据;一句永远无法成立的证伪条件使 S1 在其自述期限内不可被证伪,与披露块「两情景各给出可观测触发条件与失效阈值」不符;同一判断档内本情景触发条件写「2026-12 或 2027-01 发布」、S2 证伪句写「2026-12 与 2027-01 两月发布」,S1 证伪句的时间限定与二者口径不一致。即便按宽松读法(把 2027-01 当月发布也算入)可由(2026-11,2026-12 观测月)达成,原句仍有歧义,需改为明确发布月。
- 改句(可用证据面数字成立): 「若 2026-12 与 2027-01 两月发布的 EA_HICP_YOY 同比(对应 2026-11、2026-12 观测月,规则发布日 2026-12-16、2027-01-16,均不晚于期限 2027-02-15)连续两个月低于 3.0%,通胀粘性假设被证伪」——两个观测月在截止日均未发布,条件可观测、可触发;阈值 3.0% 与期限 2027-02-15 不变;改后披露块该句即属实。
- 备选改句(保留原时间界、更严的单次发布口径): 「若 2026-12-16 发布的 EA_HICP_YOY 同比(2026-11 观测月)低于 3.0%,通胀粘性假设被证伪」。

### MINOR(5 条,均不改变结论)

| 编号 | 位置 | 问题 | 直算依据 | 建议 |
|---|---|---|---|---|
| MINOR-1 | C1-INFL-SYNC 陈述句括注「更早月份位次有交叉」 | 字面属实但缺时间范围,易被读成近年频繁交叉 | 全史 106 个可比月中 EA 高于美国仅 2022-07 至 2023-09(15 个月)与 2026-09;2023-10 至 2026-08 连续 34 个可比月均为 EA 低于美国(F8b) | 改为「九月为 2023-09 以来首个高于美国的可比月份(2022-07 至 2023-09 曾持续高于美国)」 |
| MINOR-2 | 传导链环 1 observed_fact「BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50，合主解释」 | 两端点是该窗最小值→最大值(2026-05-04 为 2026 年内最高),未标注;月末对月末仅 +13bp(至 2.38) | BEI_10Y 2.25@02-27、2.50@05-04、2.38@05-29(I6、D11) | 注明「段内低点→峰值」或改用月末端点并给出幅度 |
| MINOR-3 | M1 环 3「组合更接近「风险收缩+利差仍高」的混合态」 | 「利差仍高」以事实位措辞出现在 E2 环,而本问证据面无日美利差序列(JGB 收益率在册未采) | series_store 无 JGB2Y / JGB5Y / JGB10Y;在场的是 USDJPY 159.35(I5) | 改为「风险收缩+日元仍处低位(USDJPY 高位)」,或把「利差」标为【假设】 |
| MINOR-4 | C1 竞争解释一「能源与进口成本的持续传导」、S2「能源基数」前提 | 能源前提未与在场证据对账;证据索引在列的 BRENT_F 未被引用 | BRENT_F@2026-11-23=88.19;近一月 116.72→88.19=−24.44%,三个月 91.62→88.19=−3.74%,12 个月 +38.86%(K6) | 在竞争解释或披露块注明油价近一月大幅回落、三个月窗内微降,对两个前提各是同向 / 反向事实 |
| MINOR-5 | S1 / S2 情景句「至 2027-01,…」 | 「至 2027-01」发布月 / 观测月口径不明: 2027-01 观测月的规则发布日 2027-02-16 晚于期限 2027-02-15 | RELEASE_RULES 月末+16 天(J0、J7) | 写成「至 2027-01 发布(2026-12 观测月)」 |

### NIT(10 条,行文或口径标注)

1. NIT-1 M1 环 2 与缺环注记「本引擎无日本融资成本/套息持仓序列」略过宽: JP_POLICY_RATE 本身即无担保隔夜拆借利率月均(一种隔夜融资成本),JGB 收益率在册未采;建议写「无日本套息持仓与中长端融资成本(国债收益率)序列」。
2. NIT-2 总判断「日本央行官方政策目标利率约 1.25」缺 % 单位(冻结日历注记为「目标水平约1.25%」;走位面 JP 行有 %)。
3. NIT-3 传导链环 3 窗口端点不一致(TIPS_10Y 止于 2026-11-19,SPX 等取 2026-11-23,NIKKEI225 止于 2026-11-20);文中已披露,共同窗 SPX −5.87% 方向不变。
4. NIT-4 传导链环 2 把 TIPS_10Y 列为区分指标,同时自陈两解释在其上预言不分立;属诚实披露,但更准确的说法是「本环无可区分指标」。
5. NIT-5 S1 情景句「两地政策面维持紧缩偏向(日本月均中枢不低于当前台阶)」地区指代混用(「两地」指美欧,括注却是日本);美欧政策面不在本问证据面,只能作假设。
6. NIT-6 披露块「已登记为待裁定残留,本轮未改引擎」属程序性声明,只读面无法核验(非错误,仅记录)。
7. NIT-7 `MAP_REPORT.md` 第 8 行写「经独立语义审查」,而该报告是裁决缺席状态下的渲染(第 217 行为「独立席位待裁」);属引擎模板文字(规程第 0 节已说明),仅记录。
8. NIT-8 C2「增长面大体平稳」只基于硬数据;快照库内软数据 UMCSENT 55.2(2026-07)→48.0(2026-10)方向相反,但不在本问计划指标面与证据索引;可把「增长面」限定为「硬数据增长面」。
9. NIT-9 「跨国跟进/背离在政策维度依本问证据不可判」限定语准确;快照库内(不在计划指标面与证据索引)另有美联储目标区间上限 3.75→4.00(2026-09-17)、欧央行存款便利利率 2.25→2.50(2026-09-16),与日本央行 2026-09-18 决议同月收紧;可选择性注明「快照库内有、本问未纳入」。
10. NIT-10 C3 把关键数字写成中文数字(约一点二五 / 六十天 / 六十六天 / 正六十七个基点 / 正七十五个基点),判断档已自陈其不在契约数字绑定之列;席位人工复算五个数均正确(1.25 / 60 / 66 / +67 / +75);建议用阿拉伯数字并带单位。

引擎面观察(不计入问题清单,非判断文字): `MAP_REPORT.md` 第 16 行标题「四地三时点环境对照」而本问仅涉美 / 欧 / 日三地。

## 6. 席位自身检查设计更正记录(为透明起见)

以下更正只涉及席位检查的设计,未改动任何输入;最终表以 `recompute_points.json` 为准。

- B25b: 初版误设「CORE_PCE 2026-07 观测缺席」;实为在库 130.148、但规则发布日 2026-08-30 晚于锚 as_of 2026-08-23 → 改为发布可见性核验。
- D11b: 初版基期日误取 2026-10-21(得 −22bp);引擎「近 30 日」窗为 2026-10-23→2026-11-20 → 改正。
- 资产窗端点: NIKKEI225 起点曾按两位小数比对而误判,改为按报告显示精度比对。
- I4: anchor_echo 实为 18 条(非 16)。
- K2: 初版变更点函数漏掉窗内首观测(无窗内前值),改为对全序列前一观测比对。
- J5: 登记调用的实参错位两版(一度被误计为命中),改正后为唯一偏离点。
- 分类标签: K1 / K2 / K3 改归⑭,K4 归入第 4 节,K5 / K6 / I6 归入第 4 节,K7 归⑩。

## 7. 复核指引(只读)

```
RUN="/tmp/r32-accept/final4/output/research_runs/20261123T193157Z_对比角度换一个_2026年11月_美国与欧元区的增长和通胀环境相比3个月前各有什"
D=/tmp/r32-accept/review4/B_round1
cd /tmp && /usr/bin/python3 -I "$D/s10_recompute.py" \
  "$RUN/root_overlay/data/daily/research_snapshot_20261123.json" "$RUN/report.json" "$RUN/agent_judgment.json" \
  "$RUN/root_overlay/config/release_calendar.json" "$RUN/root_overlay/config/metric_registry.json" "$D" \
  "$RUN/MAP_REPORT.md" "$RUN/MAP_REPORT.sha256"
# 期望输出: recompute_points=190 mismatches=1(MISMATCH J5-S1-falsifier-reachable)
```
