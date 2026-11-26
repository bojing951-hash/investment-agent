# Audit-R32 · C4 · Round-1 独立语义审查席复算记录(PROSE)

## 0 受审对象与只读面

| 项 | 值 |
|---|---|
| 席位 | independent-zero-context-seat-r32-c4-round1(零上下文独立语义审查席; 未委派子代理; 未与研判席/操作者通信; 未读取任何预审内容) |
| 审查日期 | 2026-11-24 |
| 受审稿 | agent_judgment.json(schema_version 1.1; sha256 7f9bcc62b5f1cd694c2ea08dd1d816c1dcab1e581b8f9e25ec99b45bbf227ecf) |
| 工单问题 | 2026年11月,美、欧、中、日四地的宏观环境相比三个月前,哪些经济体之间出现了明显分化?分化主要体现在哪些维度?请给出具体数据和各数据的公布时间,并说明哪些维度证据不足以下结论。 |
| 运行 | run ts_utc 20261123T235101Z; git_head 36499bb78a18dea1ff2b027074088b0ba404c3b8; evidence_asof 2026-11-23; source_snapshot_id research_snapshot_20261123 |
| 点锚 | 「三个月前」=2026-08-23;「最新一期」=2026-11-23(截止时点 research_as_of 2026-11-23T22:58:11+08:00, 即纽约 09:58、法兰克福 15:58、东京 23:58、上海 22:58) |
| 冻结输入 | release_calendar.json(v1.5.0, 18 条; sha256 e44fd2aa5ced0310c4513bf862940b937367fd5eadc0297363e950aa873a24cb); metric_registry.json(v2.8.7; sha256 fa396d22175a4814c06613c0758646d5d759c2a6eac7e0347475a46f8e59ca58); research_snapshot_20261123.json(sha256 2de337533ef5fbac55a024ad0df78cbba24bc455cbd2e4ddadc65b4d668ae403); 三文件 sha256 前 16 位与工单信封 frozen_inputs 逐项一致 |
| 引擎面 | report.json(sha256 7e76d525aa5f6809d02ec70e01d8b2ad300401398b4bf5149b7cdd84ee5353cd) |
| 渲染面(仅用于核对披露类陈述) | MAP_REPORT.md(sha256 前缀 46b61bd4d4c9ec5a) |
| 契约文本 | AGENT_SEAT_ENVELOPE.json(reader_map_contract 等字段) |
| 引擎源码文本(只读取文本、不执行) | scripts/research_contract/text_consistency.py(别名表)、scripts/research_map_planner.py(并项/补选规则)、scripts/agent_judgment.py(阻断类常量) |

## 1 方法与判据

1. 直算优先: 每点先从只读面直算并落直算值, 再与受审稿文字比对; 未凭记忆或常识补数。
2. 锚格重选: 锚格值按引擎发布纪律独立重选——取「发布日 ≤ 锚日」的最新观测; 有日历实录条目者按日历, 否则按引擎 RELEASE_RULES 推定(美国 GDP 季末+29 天、日本 GDP 季末+45 天、失业率月末+5 天、工业生产月末+15 天、CPI/核心 CPI 月末+13 天、核心 PCE 月末+30 天、中国 PMI 月末−1 天、中国 CPI/PPI 月末+9 天、日本全国 CPI 月末+20 天、东京都 CPI 月末−1 天、日本政策利率月末+5 天、DFF 观测日+1 天)。月频序列观测日为月首日, 故「三个月前锚」多为 2026-07 观测(2026-08 观测的发布日晚于锚日 2026-08-23, 不计入)。
3. 比对判据: 直算值按受审稿所载小数位四舍五入后逐位相等(相对容差 1e-9·max(1,|受审稿值|)); 日期与字符串逐字; 布尔项直判。
4. 同比基期: 同比一律以序列内上年同月/同季观测直算; 基期缺席即判「不可得」, 并核对受审稿是否如实标注。
5. 中文数字: L3 陈述使用中文数字, 本席逐句转写为阿拉伯数字后作为受审稿值录入比对。
6. 点的分类: 「比对点」=受审稿文字所载数字/日期/方向/结构性陈述的核对, 计入 recompute_points; 「辅助点」=为支撑反方攻击、披露核对或事实前提而做的直算(受审稿无对应文字), 不计入。
7. 运行方式: 脚本均位于本席目录, 以 /usr/bin/python3 -I <脚本> <路径参数…> 自 /tmp 运行; 未在数据目录内启动解释器; 引擎源码仅作文本检索, 未导入执行。

## 2 复算结果总览

- 比对点 403 点: 一致 402, 偏离 1(E25, 见第 8 节 MINOR-1)。
- 辅助点 27 点: 全部一致; 不计入 recompute_points(清单见第 4 节)。合计 430 点。
- 首轮检查口径修正: 13 组 19 点, 逐条登记于第 5 节(均为检查设计问题, 非受审稿错误)。
- 数字覆盖复扫(ASCII 边界): 受审稿内非日期数字 token 共 146 个。无同值通过点的 12 个逐一说明——0.05/0.10 为情景阈值的派生步长(派生阈值 1.28/2.90 由 C02/C03 核对); 9 为「候选池9」(T16)与「9 月初」(E 系列); 36 为「历史长度不足 36 个月」(X50); 09/10/22/23/58 为时刻与月份数字(D05 系列、E 系列); 100 为「100% 归 Agent」归属声明; 225/500 为指数名称。其余 token 均有同值通过点; 小整数(0–30)另按上下文逐个核对, 防同值巧合覆盖。

| 组 | 内容 | 比对点 | 偏离 | 辅助点 |
|---|---|---|---|---|
| A | 资产月窗两口径与盘中反弹 | 42 | 0 | 3 |
| C | 情景(阈值派生、截止日取值、互斥、期限) | 7 | 0 | 2 |
| D | 日期与截止时点(四地时刻、末观测日、截止后日期) | 12 | 0 | 0 |
| E | 能源价格对账(WTI_F/BRENT_F/现货月均价/月均值) | 29 | 1 | 0 |
| G | 增长维(GDP/失业率/工业生产/PMI/日本 GDP) | 19 | 0 | 0 |
| I | 通胀维(日/美/中通胀序列水平、同比与发布日) | 36 | 0 | 1 |
| K | 结构性陈述计数(矛盾/链条/传导环/转折/并列解释) | 14 | 0 | 3 |
| N | 类比面(扫描/有效/剔除/TOP-5/覆盖率/贡献份额/缺席特征) | 28 | 0 | 0 |
| P | 政策维(美/日政策利率、事件簇、日历实录、中国 LPR/逆回购/隔夜、注册表) | 70 | 0 | 2 |
| Q | Gate A 缺口与质量计数 | 17 | 0 | 2 |
| R | 美国三利率分解(近一月窗、12 个月窗) | 24 | 0 | 0 |
| T | 转折候选池、三转折叙述与补选项 | 19 | 0 | 2 |
| U | 发布日(日历实录/推定规则)与截止纪律 | 35 | 0 | 6 |
| V | 点值格锚格按发布规则独立重选 | 7 | 0 | 0 |
| X | 补充核对(渲染面/信封/证据索引/别名表/并项规则/计数类数字) | 44 | 0 | 6 |
| 合计 | — | 403 | 1 | 27 |

## 3 逐点复算清单(比对点 403 点)

「出处」列为只读面(文件 · 面/键), 序列值的键即「复算项」列所载的 序列ID@观测日/月; 「直算值」为本席自只读面直算, 「受审稿值」为受审稿文字所载(中文数字已转写)。

| 编号 | 出处(只读面: 文件 · 面/键) | 复算项(序列ID@观测日/月 或 字段) | 直算值 | 受审稿值 | 判定 |
|---|---|---|---|---|---|
| E01 | research_snapshot_20261123.json series_store | WTI_F 锚 obs | 2026-08-21 | 2026-08-21 | 一致 |
| E02 | research_snapshot_20261123.json series_store | WTI_F@2026-08-21 | 87.06 | 87.06 | 一致 |
| E03 | research_snapshot_20261123.json series_store | WTI_F@2026-10-30 | 104.12 | 104.12 | 一致 |
| E04 | research_snapshot_20261123.json series_store | WTI_F 10-30 vs 锚 % | 19.60 | 19.6 | 一致 |
| E05 | research_snapshot_20261123.json series_store | WTI_F@2026-11-23 | 82.02 | 82.02 | 一致 |
| E06 | research_snapshot_20261123.json series_store | WTI_F 11-23 vs 锚 % | -5.79 | -5.79 | 一致 |
| E07 | research_snapshot_20261123.json series_store | WTI_F 11-23 vs 10-30 % | -21.23 | -21.23 | 一致 |
| E08 | research_snapshot_20261123.json series_store | BRENT_F 锚 obs 2026-08-21 | 94.39 | 94.39 | 一致 |
| E09 | research_snapshot_20261123.json series_store | BRENT_F@2026-10-30 | 117.64 | 117.64 | 一致 |
| E10 | research_snapshot_20261123.json series_store | BRENT_F 10-30 vs 锚 % | 24.63 | 24.63 | 一致 |
| E11 | research_snapshot_20261123.json series_store | BRENT_F@2026-11-23 | 88.19 | 88.19 | 一致 |
| E12 | research_snapshot_20261123.json series_store | BRENT_F 11-23 vs 锚 % | -6.57 | -6.57 | 一致 |
| E13 | research_snapshot_20261123.json series_store | BRENT_F 11-23 vs 10-30 % | -25.03 | -25.03 | 一致 |
| E14 | research_snapshot_20261123.json series_store | WTI_SPOT_M@2026-08 | 83.9 | 83.9 | 一致 |
| E15 | research_snapshot_20261123.json series_store | WTI_SPOT_M@2026-10 | 102.07 | 102.07 | 一致 |
| E16 | research_snapshot_20261123.json series_store | WTI_SPOT_M 10月 vs 8月 % | 21.66 | 21.66 | 一致 |
| E17 | research_snapshot_20261123.json series_store | WTI_F 2026-08 自然月均值 | 82.45 | 82.45 | 一致 |
| E18 | research_snapshot_20261123.json series_store | WTI_F 2026-10 自然月均值 | 96.94 | 96.94 | 一致 |
| E19 | research_snapshot_20261123.json series_store | WTI_F@2026-09-16 | 102.43 | 102.43 | 一致 |
| E20 | research_snapshot_20261123.json series_store | WTI_F 09-16 vs 锚 % | 17.65 | 17.65 | 一致 |
| E21 | research_snapshot_20261123.json series_store | WTI_F@2026-09-18 | 100.30 | 100.3 | 一致 |
| E22 | research_snapshot_20261123.json series_store | WTI_F 09-18 vs 锚 % | 15.21 | 15.21 | 一致 |
| E23 | research_snapshot_20261123.json series_store | WTI_F 2026-09-01..2026-10-31 全部观测 > 锚 87.06 (n=43, min=88.28) | True | True | 一致 |
| E24 | research_snapshot_20261123.json series_store | WTI_F 11-02 起首个跌破锚的观测日 | 2026-11-09 | 2026-11-09 | 一致 |
| E25 | research_snapshot_20261123.json series_store | WTI_F 2026-11-09..11-23 全部 < 锚(受审稿『11-09 起再度跌破该锚』的字面持续性; 实测 11 个观测中 9 个低于锚, 11-12=88.74、11-13=88.56 回到锚上方) | False | True | 偏离 |
| E26 | research_snapshot_20261123.json series_store | WTI_F 2026-11-02..11-06(跌破前) 全部 > 锚 | True | True | 一致 |
| E27 | research_snapshot_20261123.json series_store | WTI_F 8 月底(锚后至 8-31)有短暂低于锚的观测 | True | True | 一致 |
| E28 | research_snapshot_20261123.json series_store | WTI_SPOT_M 末观测月 | 2026-10 | 2026-10 | 一致 |
| E29 | research_snapshot_20261123.json series_store | WTI_F 2026-09-01..2026-10-31 观测全部 > 锚(受审稿『期货 9 月初至 10 月底的观测全部高于三个月前锚』) | True | True | 一致 |
| P01 | research_snapshot_20261123.json series_store | DFEDTARU@<=2026-08-23 (obs 2026-08-23) | 3.75 | 3.75 | 一致 |
| P02 | research_snapshot_20261123.json series_store | DFEDTARU anchor obs date | 2026-08-23 | 2026-08-23 | 一致 |
| P03 | research_snapshot_20261123.json series_store | DFEDTARU@<=2026-11-23 (obs 2026-11-23) | 4.00 | 4.0 | 一致 |
| P04 | research_snapshot_20261123.json series_store | DFEDTARU latest obs date | 2026-11-23 | 2026-11-23 | 一致 |
| P05 | research_snapshot_20261123.json series_store | DFEDTARU 上限变动(bp)=(b-a)*100 | 25 | 25 | 一致 |
| P06 | research_snapshot_20261123.json series_store | DFEDTARU 窗内变动点1 日期(生效) | 2026-09-17 | 2026-09-17 | 一致 |
| P07 | research_snapshot_20261123.json series_store | DFEDTARU 变动点1 from | 3.75 | 3.75 | 一致 |
| P08 | research_snapshot_20261123.json series_store | DFEDTARU 变动点1 to | 4.00 | 4.0 | 一致 |
| P09 | research_snapshot_20261123.json series_store | DFEDTARU 变动点1 幅度(bp) | 25 | 25 | 一致 |
| P10 | research_snapshot_20261123.json series_store | 决议日=生效日前一日 | 2026-09-16 | 2026-09-16 | 一致 |
| P11 | research_snapshot_20261123.json series_store | DFEDTARU 窗内变动点0 日期(生效) | 2025-12-11 | 2025-12-11 | 一致 |
| P12 | research_snapshot_20261123.json series_store | DFEDTARU 变动点0 from | 4.00 | 4.0 | 一致 |
| P13 | research_snapshot_20261123.json series_store | DFEDTARU 变动点0 to | 3.75 | 3.75 | 一致 |
| P14 | research_snapshot_20261123.json series_store | DFEDTARU 变动点0 幅度(bp) | -25 | -25 | 一致 |
| P15 | research_snapshot_20261123.json series_store | 决议日=生效日前一日 | 2025-12-10 | 2025-12-10 | 一致 |
| P16 | research_snapshot_20261123.json series_store | DFEDTARU 近一年窗变动点数=2 | True | True | 一致 |
| P17 | research_snapshot_20261123.json series_store | DFEDTARU 近一年净变动(bp) | 0 | 0 | 一致 |
| P18 | research_snapshot_20261123.json series_store | DFF 三个月前锚 obs(发布=观测日+1 ≤ 2026-08-23 的最后观测) | 2026-08-22 | 2026-08-22 | 一致 |
| P19 | research_snapshot_20261123.json series_store | DFF@2026-08-22 | 3.63 | 3.63 | 一致 |
| P20 | research_snapshot_20261123.json series_store | DFF 最新 obs(发布=观测日+1 ≤ 2026-11-23 的最后观测) | 2026-11-19 | 2026-11-19 | 一致 |
| P21 | research_snapshot_20261123.json series_store | DFF@2026-11-19 | 3.88 | 3.88 | 一致 |
| P22 | research_snapshot_20261123.json series_store | DFF@2026-09-16 | 3.63 | 3.63 | 一致 |
| P23 | research_snapshot_20261123.json series_store | DFF@2026-09-17 | 3.88 | 3.88 | 一致 |
| P24 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2025-11 | 0.478 | 0.478 | 一致 |
| P25 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2025-12 | 0.557 | 0.557 | 一致 |
| P26 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-04 | 0.727 | 0.727 | 一致 |
| P27 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-07 | 0.978 | 0.978 | 一致 |
| P28 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-08 | 0.977 | 0.977 | 一致 |
| P29 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-09 | 1.043 | 1.043 | 一致 |
| P30 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-10 | 1.227 | 1.227 | 一致 |
| P31 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 三个月净变动(bp)=(10月-7月)*100 | 25 | 25 | 一致 |
| P32 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 近12个月净变动(bp) | 75 | 75 | 一致 |
| P33 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 自窗内首观测起算(bp) | 67 | 67 | 一致 |
| P34 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 12月窗变动点=6 个且幅度=[8,17,11,14,7,18] | True | True | 一致 |
| P35 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 2026-07 - 2026-04 (pp) | 0.251 | 0.251 | 一致 |
| P36 | release_calendar.json entries[*] | 存在日本央行 2026-09 目标条目 (决议 2026-09-18) | True | True | 一致 |
| P37 | release_calendar.json entries[*] | 生效 2026-09-24 | True | True | 一致 |
| P38 | release_calendar.json entries[*] | 目标水平 1.25 | True | True | 一致 |
| P39 | release_calendar.json entries[*] | 2026-10-30 维持条目 | True | True | 一致 |
| P40 | release_calendar.json entries[*] | 维持条目无生效日 | True | True | 一致 |
| P43 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 两决议同一 ISO 周 | True | True | 一致 |
| P44 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 两决议相隔天数 | 2 | 2 | 一致 |
| P45 | research_snapshot_20261123.json series_store | CN_LPR_1Y 锚 obs | 2026-08-20 | 2026-08-20 | 一致 |
| P46 | research_snapshot_20261123.json series_store | CN_LPR_1Y@2026-08-20 | 3.00 | 3.0 | 一致 |
| P47 | research_snapshot_20261123.json series_store | CN_LPR_1Y 最新 obs | 2026-11-20 | 2026-11-20 | 一致 |
| P48 | research_snapshot_20261123.json series_store | CN_LPR_1Y@2026-11-20 | 3.00 | 3.0 | 一致 |
| P49 | research_snapshot_20261123.json series_store | CN_LPR_1Y 序列末观测 | 2026-11-20 | 2026-11-20 | 一致 |
| P50 | research_snapshot_20261123.json series_store | CN_LPR_1Y 2026-08-20..2026-11-20 全部观测均为 3.0 (n=4) | True | True | 一致 |
| P51 | release_calendar.json entries[RC-CN-LPR-2026M11] | 日期 2026-11-20 / 09:00 | True | True | 一致 |
| P52 | release_calendar.json entries | 无 2026-08 LPR 实录条目(锚发布日属官方惯例) | True | True | 一致 |
| P53 | research_snapshot_20261123.json series_store | CN_OMO_7D 锚 obs | 2026-08-21 | 2026-08-21 | 一致 |
| P54 | research_snapshot_20261123.json series_store | CN_OMO_7D@2026-08-21 | 1.40 | 1.4 | 一致 |
| P55 | research_snapshot_20261123.json series_store | CN_OMO_7D 末观测 | 2026-10-30 | 2026-10-30 | 一致 |
| P56 | research_snapshot_20261123.json series_store | CN_OMO_7D@2026-10-30 | 1.40 | 1.4 | 一致 |
| P57 | research_snapshot_20261123.json series_store | CN_OMO_7D 末观测滞后天数(=2026-11-23-末观测) | 24 | 24 | 一致 |
| P58 | research_snapshot_20261123.json series_store | CN_OMO_7D 2026-08-21 之后全部观测=1.4 (n=34) | True | True | 一致 |
| P59 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT 首观测 | 2026-11-02 | 2026-11-02 | 一致 |
| P60 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT 末观测 | 2026-11-23 | 2026-11-23 | 一致 |
| P61 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT@末观测 | 1.25 | 1.25 | 一致 |
| P62 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT 在 2026-08-23 前无观测 | True | True | 一致 |
| P63 | research_snapshot_20261123.json series_store | series_store 无 EA_REAL_GDP_YOY | True | True | 一致 |
| P64 | research_snapshot_20261123.json series_store | series_store 无 EA_HICP_YOY | True | True | 一致 |
| P65 | research_snapshot_20261123.json series_store | series_store 无 ECB_MRO | True | True | 一致 |
| P66 | research_snapshot_20261123.json series_store | series_store 无 ECB_DFR | True | True | 一致 |
| P67 | research_snapshot_20261123.json series_store | series_store 无 BUND_10Y | True | True | 一致 |
| P68 | research_snapshot_20261123.json series_store | series_store 无 BUND_2Y | True | True | 一致 |
| P69 | research_snapshot_20261123.json series_store | series_store 无 JP_POLICY_TARGET | True | True | 一致 |
| P70 | metric_registry.json metrics[*].metric_id | 注册表无 JP_POLICY_TARGET | True | True | 一致 |
| P71 | release_calendar.json entries[*].id/kind | 冻结日历无美国政策条目、无 FOMC 纪要条目(条目 id 仅 2025SHUTDOWN 数据发布/EA-HICP/JP-BOJ/CN-LPR) | True | True | 一致 |
| P72 | report.json research_plan.policy_doc_facts | FOMC-MINUTES-2026-10 发布 2026-11-18, basis=user_directive | True | True | 一致 |
| G01 | research_snapshot_20261123.json series_store | US_REAL_GDP@2026-07 | 24611.077 | 24611.077 | 一致 |
| G02 | research_snapshot_20261123.json series_store | US_REAL_GDP@2026-04 | 24408.011 | 24408.011 | 一致 |
| G03 | research_snapshot_20261123.json series_store | US_REAL_GDP 同比 2026-07 (基期 2025-07) % | 2.07 | 2.07 | 一致 |
| G04 | research_snapshot_20261123.json series_store | US_REAL_GDP 同比 2026-04 (基期 2025-04) % | 2.19 | 2.19 | 一致 |
| G05 | research_snapshot_20261123.json series_store | US_REAL_GDP 末观测季 | 2026-07 | 2026-07 | 一致 |
| G06 | research_snapshot_20261123.json series_store | UNEMPLOYMENT@2026-07 | 4.1 | 4.1 | 一致 |
| G07 | research_snapshot_20261123.json series_store | UNEMPLOYMENT@2026-10 | 4.1 | 4.1 | 一致 |
| G08 | research_snapshot_20261123.json series_store | UNEMPLOYMENT 末观测月 | 2026-10 | 2026-10 | 一致 |
| G09 | research_snapshot_20261123.json series_store | INDPRO@2026-10 | 103.3954 | 103.3954 | 一致 |
| G10 | research_snapshot_20261123.json series_store | INDPRO@2026-07 | 103.1675 | 103.1675 | 一致 |
| G11 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-10 % | 2.15 | 2.15 | 一致 |
| G12 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-07 % | 1.25 | 1.25 | 一致 |
| G13 | research_snapshot_20261123.json series_store | INDPRO 末观测月 | 2026-10 | 2026-10 | 一致 |
| G14 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-07 | 49.2 | 49.2 | 一致 |
| G15 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-10 | 49.3 | 49.3 | 一致 |
| G16 | research_snapshot_20261123.json series_store | JP_REAL_GDP_YOY@2026-04 | 0.80 | 0.8 | 一致 |
| G17 | research_snapshot_20261123.json series_store | JP_REAL_GDP_YOY@2026-07 | 1.16 | 1.16 | 一致 |
| G18 | research_snapshot_20261123.json series_store | JP_REAL_GDP_YOY 末观测季 | 2026-07 | 2026-07 | 一致 |
| G19 | research_snapshot_20261123.json series_store | 两期 PMI 均在荣枯线下方(49.2、49.3 < 50) | True | True | 一致 |
| I01 | research_snapshot_20261123.json series_store | JP_CPI_YOY@2026-07 | 1.97 | 1.97 | 一致 |
| I02 | research_snapshot_20261123.json series_store | JP_CPI_YOY@2026-10 | 2.44 | 2.44 | 一致 |
| I03 | research_snapshot_20261123.json series_store | JP_CPI_YOY 末观测月 | 2026-10 | 2026-10 | 一致 |
| I04 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-07 | 1.85 | 1.85 | 一致 |
| I05 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-10 | 2.73 | 2.73 | 一致 |
| I06 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-06 | 1.6 | 1.6 | 一致 |
| I07 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-09 | 2.69 | 2.69 | 一致 |
| I08 | research_snapshot_20261123.json series_store | 东京都同比 2026-09 - 2026-06 (pp) | 1.09 | 1.09 | 一致 |
| I10 | research_snapshot_20261123.json series_store | CPI@2026-10 | 337.476 | 337.476 | 一致 |
| I11 | research_snapshot_20261123.json series_store | CPI@2026-07 | 332.813 | 332.813 | 一致 |
| I12 | research_snapshot_20261123.json series_store | CPI 无 2025-10 观测(同比基期缺) | True | True | 一致 |
| I13 | research_snapshot_20261123.json series_store | CPI 同比 2026-09 (基期 2025-09) % | 3.72 | 3.72 | 一致 |
| I14 | research_snapshot_20261123.json series_store | CPI 同比 2026-07 (基期 2025-07) % | 3.30 | 3.3 | 一致 |
| I15 | research_snapshot_20261123.json series_store | CPI 2026-10 为最新月且其同比不可得、2026-09 为最近有效同比 | True | True | 一致 |
| I16 | research_snapshot_20261123.json series_store | CORE_CPI@2026-10 | 339.9 | 339.9 | 一致 |
| I17 | research_snapshot_20261123.json series_store | CORE_CPI@2026-07 | 336.789 | 336.789 | 一致 |
| I18 | research_snapshot_20261123.json series_store | CORE_CPI 无 2025-10 观测 | True | True | 一致 |
| I19 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-09 % | 2.57 | 2.57 | 一致 |
| I20 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-07 % | 2.47 | 2.47 | 一致 |
| I21 | research_snapshot_20261123.json series_store | CORE_PCE@2026-09 | 130.902 | 130.902 | 一致 |
| I22 | research_snapshot_20261123.json series_store | CORE_PCE@2026-06 | 129.969 | 129.969 | 一致 |
| I23 | research_snapshot_20261123.json series_store | CORE_PCE 同比 2026-06 % | 3.04 | 3.04 | 一致 |
| I24 | research_snapshot_20261123.json series_store | CORE_PCE 同比 2026-09 % | 3.12 | 3.12 | 一致 |
| I25 | research_snapshot_20261123.json series_store | CORE_PCE 末观测月 | 2026-09 | 2026-09 | 一致 |
| I26 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-07 | 0.5 | 0.5 | 一致 |
| I27 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-10 | 0.7 | 0.7 | 一致 |
| I28 | research_snapshot_20261123.json series_store | CN_PPI_YOY@2026-07 | 3.5 | 3.5 | 一致 |
| I29 | research_snapshot_20261123.json series_store | CN_PPI_YOY@2026-10 | 5.7 | 5.7 | 一致 |
| I30 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-10 序列日期(=点值格观测日 2026-10-01; 证据索引标签 2026-10-31 为期末口径, 受审稿已披露两口径不同) | 2026-10-01 | 2026-10-01 | 一致 |
| I30b | report.json evidence_index[*].ref | 证据索引对 CN_CPI_YOY/CN_PPI_YOY 最新一期的引用标签(期末口径) | CN_CPI_YOY@2026-10-31,CN_PPI_YOY@2026-10-31 | CN_CPI_YOY@2026-10-31,CN_PPI_YOY@2026-10-31 | 一致 |
| I31 | research_snapshot_20261123.json series_store | 剪刀差 2026-07 = PPI-CPI (pp) | 3.0 | 3.0 | 一致 |
| I32 | research_snapshot_20261123.json series_store | 剪刀差 2026-10 = PPI-CPI (pp) | 5.0 | 5.0 | 一致 |
| I33 | research_snapshot_20261123.json series_store | 美国 CPI 同比 3.72(2026-09) > 3.30(2026-07) | True | True | 一致 |
| I34 | research_snapshot_20261123.json series_store | 美国核心CPI同比 2.57(2026-09) > 2.47(2026-07) | True | True | 一致 |
| I35 | research_snapshot_20261123.json series_store | 美国核心PCE同比 3.12(2026-09) > 3.04(2026-06) | True | True | 一致 |
| I36 | research_snapshot_20261123.json series_store | 日本 2.44>1.97、东京 2.73>1.85、中国CPI 0.7>0.5、PPI 5.7>3.5 | True | True | 一致 |
| T01 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-05 % | 2.8229 | 2.8229 | 一致 |
| T02 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-08 % | 2.4462 | 2.4462 | 一致 |
| T03 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-09 % | 2.5658 | 2.5658 | 一致 |
| T04 | research_snapshot_20261123.json series_store | 核心CPI同比 所引两位四位小数之差 2026-08 − 2026-05 (pp)(未舍入差 -0.376779, 四舍五入为 -0.3768) | -0.3767 | -0.3767 | 一致 |
| T04b | report.json research_plan.turning_candidates.candidates[CORE_CPI].delta | 引擎候选面 CORE_CPI delta(受审稿『三个月回落 0.3767 个百分点』) | -0.3767 | -0.3767 | 一致 |
| T05 | research_snapshot_20261123.json series_store | CPI 同比 2026-02 % | 2.434 | 2.434 | 一致 |
| T06 | research_snapshot_20261123.json series_store | CPI 同比 2026-05 % | 4.1666 | 4.1666 | 一致 |
| T07 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-01 | 0.2 | 0.2 | 一致 |
| T08 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-04 | 1.2 | 1.2 | 一致 |
| T09 | research_snapshot_20261123.json series_store | INDPRO 同比 2025-11 % | 1.7543 | 1.7543 | 一致 |
| T10 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-02 % | 0.7972 | 0.7972 | 一致 |
| T11 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-02 - 2025-11 (pp) | -0.9571 | -0.9571 | 一致 |
| T12 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-02 | 49.0 | 49.0 | 一致 |
| T13 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-05 | 50.0 | 50.0 | 一致 |
| T14 | research_snapshot_20261123.json series_store | CN_PMI_MFG 同比 2026-02 % | -2.3904 | -2.3904 | 一致 |
| T15 | research_snapshot_20261123.json series_store | CN_PMI_MFG 同比 2026-05 % | 1.0101 | 1.0101 | 一致 |
| T16 | report.json research_plan.turning_candidates.candidates | 候选池 9 项 | True | True | 一致 |
| T17 | report.json turning_candidates | 候选池 9 项的指标与窗口与正文所述一致 | True | True | 一致 |
| T20 | report.json turning_candidates | 除三项所取转折外, 其余 6 项窗口终点 ≤ 2026-05 | True | True | 一致 |
| V01 | report.json research_plan.point_values.cells | 按引擎所载发布规则独立重算: 35 个 status=ok 锚格的(观测日,值)=『发布日≤锚日的最后观测』且逐位一致 (35/35) | True | True | 一致 |
| V01b | report.json research_plan.point_values.cells | CN_POLICY_OVERNIGHT 三个月前锚: 发布日≤2026-08-23 的观测不存在(独立重算) | True | True | 一致 |
| V02 | agent_judgment.json reader_map.regions[*].anchor_echo | anchor_echo 35 项: 值与观测月=『发布日≤锚日的最后观测』(独立按发布规则重算), 逐位一致 | True | True | 一致 |
| V03 | report.json research_plan.point_values.cells | 点值格 18 格 + 缺席 4 格 | True | True | 一致 |
| V04 | report.json research_plan.point_values.cells | CORE_PCE 锚=2026-06(2026-07 发布晚于锚) | True | True | 一致 |
| V05 | report.json research_plan.point_values.cells | US_REAL_GDP 锚=2026-04(Q3 发布 2026-10-29 晚于锚) | True | True | 一致 |
| V06 | report.json research_plan.point_values.cells | JP_REAL_GDP_YOY 锚=2026-04 | True | True | 一致 |
| A01 | research_snapshot_20261123.json series_store | SPX@2026-10-23 | 7623.680176 | 7623.680176 | 一致 |
| A02 | research_snapshot_20261123.json series_store | SPX 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A03 | research_snapshot_20261123.json series_store | SPX 引擎窗(10-23→末观测) 变动% | -5.51 | -5.51 | 一致 |
| A04 | research_snapshot_20261123.json series_store | SPX 收盘窗(10-23→11-20) 变动% | -9.36 | -9.36 | 一致 |
| A05 | research_snapshot_20261123.json series_store | NIKKEI225@2026-10-23 | 62693.160000 | 62693.16 | 一致 |
| A06 | research_snapshot_20261123.json series_store | NIKKEI225 引擎窗终点观测日 | 2026-11-20 | 2026-11-20 | 一致 |
| A07 | research_snapshot_20261123.json series_store | NIKKEI225 引擎窗(10-23→末观测) 变动% | -9.98 | -9.98 | 一致 |
| A08 | research_snapshot_20261123.json series_store | NIKKEI225 收盘窗(10-23→11-20) 变动% | -9.98 | -9.98 | 一致 |
| A09 | research_snapshot_20261123.json series_store | SHCOMP@2026-10-23 | 3690.475300 | 3690.4753 | 一致 |
| A10 | research_snapshot_20261123.json series_store | SHCOMP 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A11 | research_snapshot_20261123.json series_store | SHCOMP 引擎窗(10-23→末观测) 变动% | -4.11 | -4.11 | 一致 |
| A12 | research_snapshot_20261123.json series_store | SHCOMP 收盘窗(10-23→11-20) 变动% | -4.25 | -4.25 | 一致 |
| A13 | research_snapshot_20261123.json series_store | DAX@2026-10-23 | 25181.650391 | 25181.650391 | 一致 |
| A14 | research_snapshot_20261123.json series_store | DAX 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A15 | research_snapshot_20261123.json series_store | DAX 引擎窗(10-23→末观测) 变动% | 0.11 | 0.11 | 一致 |
| A16 | research_snapshot_20261123.json series_store | DAX 收盘窗(10-23→11-20) 变动% | -1.50 | -1.5 | 一致 |
| A17 | research_snapshot_20261123.json series_store | VIX@2026-10-23 | 19.450001 | 19.450001 | 一致 |
| A18 | research_snapshot_20261123.json series_store | VIX 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A19 | research_snapshot_20261123.json series_store | VIX 引擎窗(10-23→末观测) 变动% | 38.87 | 38.87 | 一致 |
| A20 | research_snapshot_20261123.json series_store | VIX 收盘窗(10-23→11-20) 变动% | 84.52 | 84.52 | 一致 |
| A21 | research_snapshot_20261123.json series_store | NIKKEI225 序列末观测 | 2026-11-20 | 2026-11-20 | 一致 |
| A22 | research_snapshot_20261123.json series_store | NIKKEI225 在 2026-11-23 无观测 | True | True | 一致 |
| A23 | research_snapshot_20261123.json series_store | DAX@2026-11-23 | 25209.45 | 25209.45 | 一致 |
| A24 | research_snapshot_20261123.json series_store | VIX@2026-11-20 | 35.89 | 35.89 | 一致 |
| A25 | research_snapshot_20261123.json series_store | SPX 11-23 vs 11-20 % | 4.25 | 4.25 | 一致 |
| A26 | research_snapshot_20261123.json series_store | VIX 11-23 vs 11-20 % | -24.74 | -24.74 | 一致 |
| A27 | research_snapshot_20261123.json series_store | DAX 11-23 vs 11-20 % | 1.64 | 1.64 | 一致 |
| A28 | research_snapshot_20261123.json series_store | CAC40 收盘窗 % | 1.86 | 1.86 | 一致 |
| A29 | research_snapshot_20261123.json series_store | DXY 收盘窗 % | 1.96 | 1.96 | 一致 |
| A30 | research_snapshot_20261123.json series_store | DXY 引擎窗 % | 2.23 | 2.23 | 一致 |
| A31 | research_snapshot_20261123.json series_store | 引擎窗 NIKKEI225 与 SPX 跌幅落差绝对值(pp)(受审稿『两者跌幅相差四点四七个百分点』) | 4.47 | 4.47 | 一致 |
| A32 | research_snapshot_20261123.json series_store | 引擎窗 SPX 与 SHCOMP 落差(pp) | 1.40 | 1.4 | 一致 |
| A33 | research_snapshot_20261123.json series_store | 收盘窗 SPX 与 SHCOMP 落差(pp) | 5.11 | 5.11 | 一致 |
| A34 | research_snapshot_20261123.json series_store | USDJPY@2026-10-23 | 156.494 | 156.494 | 一致 |
| A35 | research_snapshot_20261123.json series_store | USDJPY@2026-11-23 | 159.347 | 159.347 | 一致 |
| A36 | research_snapshot_20261123.json series_store | USDJPY 引擎窗 % | 1.82 | 1.82 | 一致 |
| A37 | research_snapshot_20261123.json series_store | USDCNY@2026-10-23 | 6.6779 | 6.6779 | 一致 |
| A38 | research_snapshot_20261123.json series_store | USDCNY@2026-11-23 | 6.6542 | 6.6542 | 一致 |
| A39 | research_snapshot_20261123.json series_store | USDCNY 引擎窗 % | -0.35 | -0.35 | 一致 |
| A40 | research_snapshot_20261123.json series_store | 受审稿『同窗 USDJPY 156.494→159.347』两端值=引擎月窗 2026-10-23→2026-11-23 的观测(非 10-20→11-19 共同交易日窗; 该窗为 158.523→159.381, 见 out_s05_extra.txt) | True | True | 一致 |
| A44 | research_snapshot_20261123.json series_store | USDJPY 在三窗(10-20→11-19 / 10-23→11-23 / 10-23→11-20)均为美元对日元走强(方向稳健) | True | True | 一致 |
| A45 | research_snapshot_20261123.json series_store | USDCNY 在三窗均未走强(方向稳健) | True | True | 一致 |
| C01 | 直算(算术; 输入=已比对的两端值) | DFEDTARU 4.0 + 标准步长 0.25 | 4.25 | 4.25 | 一致 |
| C02 | 直算(算术; 输入=已比对的两端值) | JP_POLICY_RATE 1.227 + 0.05 后上取整到分位 | 1.28 | 1.28 | 一致 |
| C03 | 直算(算术; 输入=已比对的两端值) | CN_LPR_1Y 3.0 - 0.10 | 2.90 | 2.9 | 一致 |
| C04 | research_snapshot_20261123.json series_store | 截止日 DFEDTARU 4.0 未达 4.25 | True | True | 一致 |
| C05 | research_snapshot_20261123.json series_store | 截止日 JP_POLICY_RATE 1.227 < 1.28 | True | True | 一致 |
| C06 | research_snapshot_20261123.json series_store | 截止日 CN_LPR_1Y 3.0 > 2.90 | True | True | 一致 |
| C08 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 研究截止 2026-11-23 + 3 个日历月(年月进位后日取 23) | 2027-02-23 | 2027-02-23 | 一致 |
| N01 | report.json steps[S6_analog].envelope.data.candidates | scanned | 1871 | 1871 | 一致 |
| N02 | report.json steps[S6_analog].envelope.data.candidates | valid | 74 | 74 | 一致 |
| N03 | report.json steps[S6_analog].envelope.data.candidates | dropped_insufficient | 1785 | 1785 | 一致 |
| N04 | report.json steps[S6_analog].envelope.data.candidates | dropped_overlap | 12 | 12 | 一致 |
| N05 | report.json steps[S6_analog].envelope.data.candidates | valid+insufficient+overlap = scanned | 1871 | 1871 | 一致 |
| N06 | report.json steps[S6_analog].envelope.data.top[*].candidate_month | TOP-5 顺序 | 2025-03,2022-06,2023-10,2021-02,2020-01 | 2025-03,2022-06,2023-10,2021-02,2020-01 | 一致 |
| N07 | report.json steps[S6_analog].envelope.data.sort_basis | 排序依据=缺席特征数优先、其后距离 | True | True | 一致 |
| N08 | report.json steps[S6_analog].envelope.data.state_vector.growth.coverage | coverage growth | 0.17 | 0.17 | 一致 |
| N09 | report.json steps[S6_analog].envelope.data.state_vector.inflation.coverage | coverage inflation | 0.33 | 0.33 | 一致 |
| N10 | report.json steps[S6_analog].envelope.data.state_vector.rates.coverage | coverage rates | 0.75 | 0.75 | 一致 |
| N11 | report.json steps[S6_analog].envelope.data.state_vector.credit.coverage | coverage credit | 0.50 | 0.5 | 一致 |
| N12 | report.json steps[S6_analog].envelope.data.state_vector.volatility.coverage | coverage volatility | 1.00 | 1.0 | 一致 |
| N13 | report.json steps[S6_analog].envelope.data.state_vector.valuation.coverage | coverage valuation | 0.50 | 0.5 | 一致 |
| N14 | report.json steps[S6_analog].envelope.data.top[0].dims.volatility.contribution_share | 首位候选贡献份额 pct volatility | 42.13 | 42.13 | 一致 |
| N15 | report.json steps[S6_analog].envelope.data.top[0].dims.rates.contribution_share | 首位候选贡献份额 pct rates | 40.66 | 40.66 | 一致 |
| N16 | report.json steps[S6_analog].envelope.data.top[0].dims.inflation.contribution_share | 首位候选贡献份额 pct inflation | 10.54 | 10.54 | 一致 |
| N17 | report.json steps[S6_analog].envelope.data.top[0].dims.valuation.contribution_share | 首位候选贡献份额 pct valuation | 6.67 | 6.67 | 一致 |
| N18 | report.json steps[S6_analog].envelope.data.top[0].dims.credit.contribution_share | 首位候选贡献份额 pct credit | 0.00 | 0.0 | 一致 |
| N19 | report.json steps[S6_analog].envelope.data.top[0].dims.growth.contribution_share | 首位候选贡献份额 pct growth | 0.00 | 0.0 | 一致 |
| N20 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | 锚点月缺席特征数 | 12 | 12 | 一致 |
| N21 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | 缺席特征名单(排序) | CORE_CPI_yoy,CPI_yoy,FED_FUNDS_d12m,FED_FUNDS_level,GDP_yoy,HY_IG_gap_d12m,HY_OAS_d12m,INDPRO_yoy,NFP_3m_chg,RSAFS_yoy,SPX_PE_TTM_level,UNEMPLOYMENT_level | CORE_CPI_yoy,CPI_yoy,FED_FUNDS_d12m,FED_FUNDS_level,GDP_yoy,HY_IG_gap_d12m,HY_OAS_d12m,INDPRO_yoy,NFP_3m_chg,RSAFS_yoy,SPX_PE_TTM_level,UNEMPLOYMENT_level | 一致 |
| N22 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | HY_IG_gap_d12m/HY_OAS_d12m 属历史长度不足 | True | True | 一致 |
| N23 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | CORE_CPI_yoy/CPI_yoy/GDP_yoy/SPX_PE_TTM_level 属序列止于锚前两个月 | True | True | 一致 |
| N24 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | FED_FUNDS_*/INDPRO_yoy/NFP_3m_chg/RSAFS_yoy/UNEMPLOYMENT_level 属锚点月无观测(止于锚前一月) | True | True | 一致 |
| N25 | report.json steps[S6_analog].envelope.data.top[0].aftermath | 事后表现四项 | SPX,UST_10Y,DXY,GOLD_F | SPX,UST_10Y,DXY,GOLD_F | 一致 |
| N26 | report.json steps[S6_analog].envelope.data.research_mode_gate | 描述性可用/事件研究被阻断 | True | True | 一致 |
| N27 | report.json steps[S6_analog].envelope.data.anchor_month | anchor_month | 2026-11 | 2026-11 | 一致 |
| N28 | report.json steps[S6_analog].envelope.data.feature_window_months | feature_window_months | 12 | 12 | 一致 |
| R01 | research_snapshot_20261123.json series_store | 名义=实际+盈亏平衡 @2026-11-19 残差(bp) | 0.0 | 0.0 | 一致 |
| R02 | research_snapshot_20261123.json series_store | UST_10Y@2026-10-20 在场 | yes | yes | 一致 |
| R03 | research_snapshot_20261123.json series_store | TIPS_10Y@2026-10-20 在场 | yes | yes | 一致 |
| R04 | research_snapshot_20261123.json series_store | BEI_10Y@2026-10-20 在场 | yes | yes | 一致 |
| R05 | research_snapshot_20261123.json series_store | 近一月窗 UST_10Y 变动(bp) | -8.0 | -8.0 | 一致 |
| R06 | research_snapshot_20261123.json series_store | 近一月窗 TIPS_10Y 变动(bp) | 11.0 | 11.0 | 一致 |
| R07 | research_snapshot_20261123.json series_store | 近一月窗 BEI_10Y 变动(bp) | -19.0 | -19.0 | 一致 |
| R08 | research_snapshot_20261123.json series_store | 近一月窗恒等残差(bp) | 0.0 | 0.0 | 一致 |
| R09 | research_snapshot_20261123.json series_store | 12月窗 UST_10Y 变动(bp) | 91.0 | 91.0 | 一致 |
| R10 | research_snapshot_20261123.json series_store | 12月窗 TIPS_10Y 变动(bp) | 102.0 | 102.0 | 一致 |
| R11 | research_snapshot_20261123.json series_store | 12月窗 BEI_10Y 变动(bp) | -11.0 | -11.0 | 一致 |
| R12 | research_snapshot_20261123.json series_store | 12月窗恒等残差(bp) | 0.0 | 0.0 | 一致 |
| R13 | research_snapshot_20261123.json series_store | BEI_10Y 序列末观测日 | 2026-11-20 | 2026-11-20 | 一致 |
| R14 | research_snapshot_20261123.json series_store | BEI_10Y@末观测 | 2.15 | 2.15 | 一致 |
| R15 | research_snapshot_20261123.json series_store | TIPS_10Y 序列末观测日 | 2026-11-19 | 2026-11-19 | 一致 |
| R16 | research_snapshot_20261123.json series_store | UST_10Y 序列末观测日 | 2026-11-19 | 2026-11-19 | 一致 |
| R17 | research_snapshot_20261123.json series_store | UST_10Y@2026-10-23 | 5.00 | 5.0 | 一致 |
| R18 | research_snapshot_20261123.json series_store | 近一月共同交易日窗内(10-20→11-19)DFEDTARU 无变动 | True | True | 一致 |
| R19 | research_snapshot_20261123.json series_store | 近一月窗实际利率为名义利率的唯一上行分量 | True | True | 一致 |
| R20 | research_snapshot_20261123.json series_store | 12月窗实际利率为主导分量(\|+102\|>\|−11\|) | True | True | 一致 |
| R21 | research_snapshot_20261123.json series_store | 近一月窗盈亏平衡降幅(19bp)大于实际上行幅度(11bp) | True | True | 一致 |
| R_BEI_10Y_1 | research_snapshot_20261123.json series_store | BEI_10Y@2026-11-19 | 2.16 | 2.16 | 一致 |
| R_TIPS_10Y_1 | research_snapshot_20261123.json series_store | TIPS_10Y@2026-11-19 | 2.88 | 2.88 | 一致 |
| R_UST_10Y_1 | research_snapshot_20261123.json series_store | UST_10Y@2026-11-19 | 5.04 | 5.04 | 一致 |
| D01 | agent_judgment.json 全文日期扫描 | 晚于研究截止日 2026-11-23 的日期(应仅为情景期限) | 2027-02-23,2027-02-28 | 2027-02-23,2027-02-28 | 一致 |
| D02 | research_snapshot_20261123.json series_store | 受审稿所用 34 条序列的末观测日均 ≤ 2026-11-23 | True | True | 一致 |
| D03 | research_snapshot_20261123.json research_as_of | research_as_of | 2026-11-23T22:58:11+08:00 | 2026-11-23T22:58:11+08:00 | 一致 |
| D04 | report.json research_plan.cutoff | cutoff | 2026-11-23 | 2026-11-23 | 一致 |
| D05_Berlin | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 法兰克福 当地时刻 | 15:58:11 | 15:58:11 | 一致 |
| D05_New_York | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 纽约 当地时刻 | 09:58:11 | 09:58:11 | 一致 |
| D05_Shanghai | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 上海 当地时刻 | 22:58:11 | 22:58:11 | 一致 |
| D05_Tokyo | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 东京 当地时刻 | 23:58:11 | 23:58:11 | 一致 |
| D06 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 研究截止 2026-11-23 - 3 个日历月(日取 23) | 2026-08-23 | 2026-08-23 | 一致 |
| D07 | report.json research_plan.point_values.cells | 三个月前锚 as_of 全部 = 2026-08-23 | True | True | 一致 |
| D08 | report.json research_plan.point_values.cells | 最新一期锚 as_of 全部 = 2026-11-23 | True | True | 一致 |
| D09 | report.json research_plan.point_anchors | 点锚定义: 3个月前=2026-08-23, 最新一期=2026-11-23 | True | True | 一致 |
| K04 | report.json contract_verification.verdicts[*](status=STALE) | STALE 项的指标 | CORE_PCE,US_REAL_GDP | CORE_PCE,US_REAL_GDP | 一致 |
| K05 | report.json contract_verification.verdicts[*] | STALE 两项数值直读一致(value==expected) | True | True | 一致 |
| K06 | report.json contract_verification | n_contradictions=4 | True | True | 一致 |
| K07 | agent_judgment.json l3.mechanism_chains | 机制链条数 | 2 | 2 | 一致 |
| K08 | agent_judgment.json l4.scenarios | 情景数 | 2 | 2 | 一致 |
| K09 | agent_judgment.json reader_map.transmission[*].links | 传导链条数/环数 | 1 | 1 | 一致 |
| K10 | agent_judgment.json reader_map.transmission[0].links | 传导环数 | 3 | 3 | 一致 |
| K11 | agent_judgment.json reader_map.transmission[0].links[*].face_off_verdict | 三环裁定均为『尚不能区分』 | True | True | 一致 |
| K12 | agent_judgment.json reader_map.transmission[0].links[*].distinguishing_metric | 区分指标 | TIPS_10Y,BEI_10Y,VIX | TIPS_10Y,BEI_10Y,VIX | 一致 |
| K13 | agent_judgment.json l3.contradictions[*].competing_explanations | 四条矛盾陈述各含 2 种并列解释且均带【假设】 | True | True | 一致 |
| K14 | agent_judgment.json reader_map.history_periods | 历史类比取零段 | True | True | 一致 |
| K15 | agent_judgment.json reader_map.turnings | 转折数 | 3 | 3 | 一致 |
| K16 | agent_judgment.json reader_map.turnings[*] | 三转折为不同指标-月且跨两维度(通胀×2+政策×1) | True | True | 一致 |
| K17 | agent_judgment.json l4.scenarios[*] | 两情景互斥(A 需 DFEDTARU≥4.25, B 需 ≤4) | True | True | 一致 |
| Q01 | research_snapshot_20261123.json gate_a.status | status | DEGRADED | DEGRADED | 一致 |
| Q02 | research_snapshot_20261123.json gate_a.core_missing | core_missing 项数 | 0 | 0 | 一致 |
| Q03 | research_snapshot_20261123.json gate_a.noncore_missing | 非核心缺口 10 项(排序) | BUND_10Y,BUND_2Y,CN_OMO_7D,CN_POLICY_OVERNIGHT,EA_HICP_YOY,EA_REAL_GDP_YOY,ECB_DFR,ECB_MRO,JP_CPI_TOKYO_YOY,JP_REAL_GDP_YOY | BUND_10Y,BUND_2Y,CN_OMO_7D,CN_POLICY_OVERNIGHT,EA_HICP_YOY,EA_REAL_GDP_YOY,ECB_DFR,ECB_MRO,JP_CPI_TOKYO_YOY,JP_REAL_GDP_YOY | 一致 |
| Q04 | research_snapshot_20261123.json gate_a.noncore_degraded | 非核心降级 6 项(排序) | CN_SF_FLOW,JTSJOL,M2SL,SPX_EPS,SPX_PE_TTM,US_REAL_GDP | CN_SF_FLOW,JTSJOL,M2SL,SPX_EPS,SPX_PE_TTM,US_REAL_GDP | 一致 |
| Q07 | research_snapshot_20261123.json quality.counts | PASS 计数 | 72 | 72 | 一致 |
| Q08 | research_snapshot_20261123.json quality.counts | DEGRADED 计数 | 7 | 7 | 一致 |
| Q09 | research_snapshot_20261123.json quality.counts | FAIL 计数 | 0 | 0 | 一致 |
| Q10 | research_snapshot_20261123.json quality.missing_core | missing_core 项数 | 0 | 0 | 一致 |
| Q11 | report.json evidence_index | 证据索引行数 | 69 | 69 | 一致 |
| Q12 | research_snapshot_20261123.json gate_a.noncore_missing | 被列入缺口的 CN_OMO_7D/CN_POLICY_OVERNIGHT/JP_CPI_TOKYO_YOY/JP_REAL_GDP_YOY 在 series_store 有存量观测 | True | True | 一致 |
| Q13 | research_snapshot_20261123.json gate_a.noncore_missing | 六项欧元区序列在 series_store 缺席且 sources_status.ea 含 MISSING | True | True | 一致 |
| Q14 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: JP_CPI_TOKYO_YOY | True | True | 一致 |
| Q15 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: JP_REAL_GDP_YOY | True | True | 一致 |
| Q16 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: CN_OMO_7D | True | True | 一致 |
| Q17 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: CN_POLICY_OVERNIGHT | True | True | 一致 |
| Q18 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: WTI_SPOT_M | True | True | 一致 |
| Q19 | report.json evidence_index × agent_judgment evidence_refs | L3/L4 全部 evidence_refs 的指标均在证据索引内 (n_refs=46) | True | True | 一致 |
| U01 | report.json research_plan.point_values.cells | US_REAL_GDP[anc].publication_date(=2026-07-29; 规则季末+29天自 period_end 2026-06-30 重算=2026-07-29) | 2026-07-29 | 2026-07-29 | 一致 |
| U02 | report.json research_plan.point_values.cells | US_REAL_GDP[lat].publication_date(=2026-10-29; 规则季末+29天自 period_end 2026-09-30 重算=2026-10-29) | 2026-10-29 | 2026-10-29 | 一致 |
| U03 | report.json research_plan.point_values.cells | UNEMPLOYMENT[anc].publication_date(=2026-08-05; 规则月末+5天自 period_end 2026-07-31 重算=2026-08-05) | 2026-08-05 | 2026-08-05 | 一致 |
| U04 | report.json research_plan.point_values.cells | UNEMPLOYMENT[lat].publication_date(=2026-11-05; 规则月末+5天自 period_end 2026-10-31 重算=2026-11-05) | 2026-11-05 | 2026-11-05 | 一致 |
| U05 | report.json research_plan.point_values.cells | INDPRO[anc].publication_date(=2026-08-15; 规则月末+15天自 period_end 2026-07-31 重算=2026-08-15) | 2026-08-15 | 2026-08-15 | 一致 |
| U06 | report.json research_plan.point_values.cells | INDPRO[lat].publication_date(=2026-11-15; 规则月末+15天自 period_end 2026-10-31 重算=2026-11-15) | 2026-11-15 | 2026-11-15 | 一致 |
| U07 | report.json research_plan.point_values.cells | CPI[anc].publication_date(=2026-08-13; 规则月末+13天自 period_end 2026-07-31 重算=2026-08-13) | 2026-08-13 | 2026-08-13 | 一致 |
| U08 | report.json research_plan.point_values.cells | CPI[lat].publication_date(=2026-11-13; 规则月末+13天自 period_end 2026-10-31 重算=2026-11-13) | 2026-11-13 | 2026-11-13 | 一致 |
| U09 | report.json research_plan.point_values.cells | CORE_CPI[anc].publication_date(=2026-08-13; 规则月末+13天自 period_end 2026-07-31 重算=2026-08-13) | 2026-08-13 | 2026-08-13 | 一致 |
| U10 | report.json research_plan.point_values.cells | CORE_CPI[lat].publication_date(=2026-11-13; 规则月末+13天自 period_end 2026-10-31 重算=2026-11-13) | 2026-11-13 | 2026-11-13 | 一致 |
| U11 | report.json research_plan.point_values.cells | CORE_PCE[anc].publication_date(=2026-07-30; 规则月末+30天自 period_end 2026-06-30 重算=2026-07-30) | 2026-07-30 | 2026-07-30 | 一致 |
| U12 | report.json research_plan.point_values.cells | CORE_PCE[lat].publication_date(=2026-10-30; 规则月末+30天自 period_end 2026-09-30 重算=2026-10-30) | 2026-10-30 | 2026-10-30 | 一致 |
| U13 | report.json research_plan.point_values.cells | DFF[anc].publication_date(=2026-08-23; 规则观测日+1天自 period_end 2026-08-22 重算=2026-08-23) | 2026-08-23 | 2026-08-23 | 一致 |
| U14 | report.json research_plan.point_values.cells | DFF[lat].publication_date(=2026-11-20; 规则观测日+1天自 period_end 2026-11-19 重算=2026-11-20) | 2026-11-20 | 2026-11-20 | 一致 |
| U15 | report.json research_plan.point_values.cells | CN_PMI_MFG[anc].publication_date(=2026-07-30; 规则月末-1天自 period_end 2026-07-31 重算=2026-07-30) | 2026-07-30 | 2026-07-30 | 一致 |
| U16 | report.json research_plan.point_values.cells | CN_PMI_MFG[lat].publication_date(=2026-10-30; 规则月末-1天自 period_end 2026-10-31 重算=2026-10-30) | 2026-10-30 | 2026-10-30 | 一致 |
| U17 | report.json research_plan.point_values.cells | CN_CPI_YOY[anc].publication_date(=2026-08-09; 规则月末+9天自 period_end 2026-07-31 重算=2026-08-09) | 2026-08-09 | 2026-08-09 | 一致 |
| U18 | report.json research_plan.point_values.cells | CN_CPI_YOY[lat].publication_date(=2026-11-09; 规则月末+9天自 period_end 2026-10-31 重算=2026-11-09) | 2026-11-09 | 2026-11-09 | 一致 |
| U19 | report.json research_plan.point_values.cells | CN_PPI_YOY[anc].publication_date(=2026-08-09; 规则月末+9天自 period_end 2026-07-31 重算=2026-08-09) | 2026-08-09 | 2026-08-09 | 一致 |
| U20 | report.json research_plan.point_values.cells | CN_PPI_YOY[lat].publication_date(=2026-11-09; 规则月末+9天自 period_end 2026-10-31 重算=2026-11-09) | 2026-11-09 | 2026-11-09 | 一致 |
| U21 | report.json research_plan.point_values.cells | JP_REAL_GDP_YOY[anc].publication_date(=2026-08-14; 规则季末+45天自 period_end 2026-06-30 重算=2026-08-14) | 2026-08-14 | 2026-08-14 | 一致 |
| U22 | report.json research_plan.point_values.cells | JP_REAL_GDP_YOY[lat].publication_date(=2026-11-14; 规则季末+45天自 period_end 2026-09-30 重算=2026-11-14) | 2026-11-14 | 2026-11-14 | 一致 |
| U23 | report.json research_plan.point_values.cells | JP_CPI_YOY[anc].publication_date(=2026-08-20; 规则月末+20天自 period_end 2026-07-31 重算=2026-08-20) | 2026-08-20 | 2026-08-20 | 一致 |
| U24 | report.json research_plan.point_values.cells | JP_CPI_YOY[lat].publication_date(=2026-11-20; 规则月末+20天自 period_end 2026-10-31 重算=2026-11-20) | 2026-11-20 | 2026-11-20 | 一致 |
| U25 | report.json research_plan.point_values.cells | JP_CPI_TOKYO_YOY[anc].publication_date(=2026-07-30; 规则月末-1天自 period_end 2026-07-31 重算=2026-07-30) | 2026-07-30 | 2026-07-30 | 一致 |
| U26 | report.json research_plan.point_values.cells | JP_CPI_TOKYO_YOY[lat].publication_date(=2026-10-30; 规则月末-1天自 period_end 2026-10-31 重算=2026-10-30) | 2026-10-30 | 2026-10-30 | 一致 |
| U27 | report.json research_plan.point_values.cells | JP_POLICY_RATE[anc].publication_date(=2026-08-05; 规则月末+5天自 period_end 2026-07-31 重算=2026-08-05) | 2026-08-05 | 2026-08-05 | 一致 |
| U28 | report.json research_plan.point_values.cells | JP_POLICY_RATE[lat].publication_date(=2026-11-05; 规则月末+5天自 period_end 2026-10-31 重算=2026-11-05) | 2026-11-05 | 2026-11-05 | 一致 |
| U29 | report.json research_plan.point_values.cells | 所引发布日(锚格)全部 ≤ 2026-08-23 | True | True | 一致 |
| U30 | report.json research_plan.point_values.cells | 所引发布日(最新一期)全部 ≤ 2026-11-23 | True | True | 一致 |
| U31 | report.json research_plan.point_values.cells | 锚格观测日全部 ≤ 2026-08-23 | True | True | 一致 |
| U32 | report.json research_plan.point_values.cells | 最新一格观测日全部 ≤ 2026-11-23 | True | True | 一致 |
| U33 | report.json research_plan.point_values.cells | 受审稿所称『引擎推定规则、非日历实录』: 除 CN_LPR_1Y 最新一期外, 所引发布日的 publication_basis 不含 calendar: | True | True | 一致 |
| U34 | report.json research_plan.point_values.cells | 东京都CPI/美国GDP 发布口径含『官方实测锚』 | True | True | 一致 |
| U35 | report.json research_plan.point_values.cells | DFEDTARU 发布口径=决议日当日公布、观测日=序列打印日(2026-08-23 / 2026-11-23) | True | True | 一致 |
| X04 | scripts/research_contract/text_consistency.py ALIASES | 文本一致性别名表未收录 JP_CPI_*、JP_REAL_GDP_YOY、EA_* (受审稿引擎缺口披露①) | True | True | 一致 |
| X05 | scripts/research_contract/text_consistency.py ALIASES | 别名表含美国『CPI』『GDP』别名(JP_CPI_*/JP_REAL_GDP_YOY 子串会被绑定到美国同名序列) | True | True | 一致 |
| X06 | MAP_REPORT.md / FULL_REPORT.md / report.md | verdict_note 字段出现次数(受审稿引擎缺口披露⑤: 不进渲染) | 0,0,0 | 0,0,0 | 一致 |
| X07 | MAP_REPORT.md | 读者所见裁定为 face_off_verdict 标签(『尚不能区分』渲染 ≥3 处) | True | True | 一致 |
| X08 | report.json steps[S7_mode_gate].envelope.gate | 类比研究模式门: 描述性可用、事件研究被阻断(受审稿历史零段注记) | True | True | 一致 |
| X09 | report.json steps[S6_analog].envelope.data.sort_basis | 类比排序依据=缺席特征数优先、其后距离, 名次非纯距离序 | True | True | 一致 |
| X10 | report.json research_plan.as_of_declared.bare_year_month | 问句含显式日历月(受审稿引擎缺口披露④) | 2026年11月 | 2026年11月 | 一致 |
| X11 | report.json notes[0] | 计划注记『地图计划指标缺数』所列指标数(受审稿: 十九) | 19 | 19 | 一致 |
| X12 | report.json notes[0] × research_plan.point_values.cells | 其中在点值格有值的指标数(受审稿: 十五) | 15 | 15 | 一致 |
| X13 | release_calendar.json version | 冻结发布日历版本(受审稿: v1.5.0) | 1.5.0 | 1.5.0 | 一致 |
| X14 | report.json research_plan.regions×point_values.cells × scripts/agent_judgment.py BLOCKING_BLOCKED_CLASSES | 交付门: 地区×维度组零 ok 格(map_core_dimension_missing 属阻断类)——受审稿『引擎交付门以核心维度缺数判为不可交付』 | True | True | 一致 |
| X15 | scripts/research_map_planner.py 并项补选口径 × MAP_REPORT.md | 引擎并项规则=同维度且观测窗重叠的转折计同一轮; 补选行标注『引擎补选』(受审稿转折取舍注记) | True | True | 一致 |
| X18 | research_snapshot_20261123.json series_store.VIX@2026-11-23 | VIX 引擎窗末值(受审稿『VIX +38.87%(19.45→27.01)』) | 27.01 | 27.01 | 一致 |
| X20 | metric_registry.json / report.json research_plan (含『换锚』字样的引擎注记) | 隔夜利率注记含 2026-11-02 换锚后的操作目标锚(受审稿转述) | True | True | 一致 |
| X19 | report.json research_plan.point_values.cells[CN_OMO_7D].anchors[最新一期].freshness* | 七天逆回购最新一格: freshness=stale、freshness_lag_days=24、freshness_window_days=10(受审稿『引擎注记为过期: 末观测滞后二十四天、超出十天发布频率窗口』) | True | True | 一致 |
| X25 | research_snapshot_20261123.json series_store.CORE_CPI 2026-08 观测 | CORE_CPI 2026-08 观测日(受审稿『窗口终点 2026-08-01 略早于三个月前锚』) | 2026-08-01 | 2026-08-01 | 一致 |
| X26 | research_snapshot_20261123.json series_store.CORE_PCE 末观测 | CORE_PCE 最新水平观测日(受审稿『观测 2026-09-01』/证据索引引用 CORE_PCE@2026-09-01) | 2026-09-01 | 2026-09-01 | 一致 |
| X27 | report.json research_plan.us_rates_trio.window.from | 共同交易日三利率窗起(受审稿『近一月共同交易日窗(2026-10-20→2026-11-19)』) | 2026-10-20 | 2026-10-20 | 一致 |
| X28 | report.json research_plan.us_rates_trio.window_12m.from | 12 个月窗起(受审稿『12 个月窗(2025-11-19→2026-11-19)』) | 2025-11-19 | 2025-11-19 | 一致 |
| X29 | report.json research_plan.asset_moves.window_rule | 资产月窗规则含 2026-10-23 与 2026-11-23(受审稿『引擎近一月窗(2026-10-23→2026-11-23)』) | True | True | 一致 |
| X30 | report.json research_plan.policy_doc_facts[0].published_on | FOMC 2026年10月会议纪要发布日(受审稿『2026-11-18 发布』) | 2026-11-18 | 2026-11-18 | 一致 |
| X31 | report.json run.ts_utc | 运行标识(受审稿『降级面开放问句 20261123T235101Z』) | 20261123T235101Z | 20261123T235101Z | 一致 |
| X32 | report.json run.evidence_gate.source_snapshot_id | 证据门源快照(受审稿『全部取自本工单冻结快照 research_snapshot_20261123』) | research_snapshot_20261123 | research_snapshot_20261123 | 一致 |
| X34 | research_snapshot_20261123.json series_store.VIX@2026-10-23 | VIX 引擎窗起值两位小数(受审稿『19.45→27.01』『19.45→35.89』) | 19.45 | 19.45 | 一致 |
| X35 | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].decision* | 日本央行 2026-09 决议日(受审稿『2026-09-18 决议』) | 2026-09-18 | 2026-09-18 | 一致 |
| X36 | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].effective* | 日本央行 2026-09 生效日(受审稿『2026-09-24 生效』) | 2026-09-24 | 2026-09-24 | 一致 |
| X37 | MAP_REPORT.md『政策一年窗路径』面板 × snapshot.series_store.JP_POLICY_RATE | 引擎『政策一年窗路径』面板载有日本无担保隔夜拆借利率窗路径(受审稿称 +75bp 与该面板同口径); 独立复算 2025-11 月均 0.478→2026-10 月均 1.227 = +74.9bp | True | True | 一致 |
| X38 | metric_registry.json metrics[JP_REAL_GDP_YOY].frequency | 日本实际 GDP 同比为季频(受审稿『JP_REAL_GDP_YOY 仅季频』) | True | True | 一致 |
| X39 | AGENT_SEAT_ENVELOPE.json reader_map_contract | 契约对历史类比段数设 0..3 上限(受审稿『契约允许 0..3 段』) | True | True | 一致 |
| X40 | report.json agent_judgment.schema_version | 研判档 schema 版本(受审稿 schema_version 1.1) | 1.1 | 1.1 | 一致 |
| X21 | report.json research_plan.point_values.cells[CN_CPI_YOY].anchors[3个月前].observation_date × snapshot.series_store.CN_CPI_YOY(按引擎发布规则月末+9天独立重算) | CN_CPI_YOY 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X22 | report.json research_plan.point_values.cells[CN_PPI_YOY].anchors[3个月前].observation_date × snapshot.series_store.CN_PPI_YOY(按引擎发布规则月末+9天独立重算) | CN_PPI_YOY 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X23 | report.json research_plan.point_values.cells[UNEMPLOYMENT].anchors[3个月前].observation_date × snapshot.series_store.UNEMPLOYMENT(按引擎发布规则月末+5天独立重算) | UNEMPLOYMENT 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X24 | report.json research_plan.point_values.cells[CN_PMI_MFG].anchors[3个月前].observation_date × snapshot.series_store.CN_PMI_MFG(按引擎发布规则月末-1天独立重算) | CN_PMI_MFG 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X33 | report.json evidence_index[*].kind × steps[S3_*].envelope.snapshot_id | 证据索引 69 行 = snapshot_fact 44 行 + s3_envelope 25 行, 且 S3 步信封源快照 = research_snapshot_20261123(与受审稿『全部取自本工单冻结快照』相容) | True | True | 一致 |
| X41 | research_snapshot_20261123.json gate_a.noncore_missing_detail | 缺口明细四组归类与受审稿数据面注记逐指标一致(ea:MISSING×6 / 注册表未登记×2 / 档内无记录×1 / FRED_JP_GDP×1) | True | True | 一致 |
| X43 | report.json research_plan.point_values.cells[CN_CPI_YOY].anchors[3个月前].observation_date | CN_CPI_YOY 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X44 | report.json research_plan.point_values.cells[CN_PPI_YOY].anchors[3个月前].observation_date | CN_PPI_YOY 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X45 | report.json research_plan.point_values.cells[UNEMPLOYMENT].anchors[3个月前].observation_date | UNEMPLOYMENT 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X46 | report.json research_plan.point_values.cells[CN_PMI_MFG].anchors[3个月前].observation_date | CN_PMI_MFG 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X47 | report.json | research_plan.point_values.cells 数量(与信封 reader_map_contract.engine_faces.point_values_cells 同值); 受审稿 agent_declaration.basis: 点值格(18格 | 18 | 18 | 一致 |
| X48 | report.json | research_plan.point_values.absent 数量(与信封 point_values_absent 同值: EA_REAL_GDP_YOY/EA_HICP_YOY/ECB_MRO/ECB_DFR); 受审稿: 另4格序列缺席 | 4 | 4 | 一致 |
| X49 | snapshot.series_store | JP_POLICY_RATE 2025-12 月均→2026-10 月均 变动(bp); 受审稿 quality_gate_notes[6]: 仅自窗内首观测(2025-12 月均 0.557)起算为 +67bp | 67.0 | 67 | 一致 |
| X50 | report.json | S6_analog.features_dropped_at_anchor 的 HY_IG_gap_d12m/HY_OAS_d12m 均含『hist_25<36点(=36个月史…)』且 normalization.min_history_months=36; 受审稿 history_zero_case_note: 历史长度不足 36 个月——HY_IG_gap_d12m、HY_OAS_d12m | True | True | 一致 |

## 4 辅助核对点(不计入比对点)

以下各点为事实前提或反方攻击所需直算(星期/天数、渲染面「近30日」窗数值、步骤面状态、跨面残差、冻结输入完整性等), 受审稿无对应文字, 故不计入比对点; 全部一致。

| 编号 | 出处(只读面: 文件 · 面/键) | 复算项(序列ID@观测日/月 或 字段) | 直算值 | 受审稿值 | 判定 |
|---|---|---|---|---|---|
| P41 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-09-16 星期 | Wednesday | Wednesday | 辅助(不计入) |
| P42 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-09-18 星期 | Friday | Friday | 辅助(不计入) |
| I09 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY 序列首观测 | 2026-01 | 2026-01 | 辅助(不计入) |
| T18 | research_snapshot_20261123.json series_store | CN_PPI_YOY@2026-02 / @2026-05 (与引擎候选面 value_before/value_after) | 0.0 | 0.0 | 辅助(不计入) |
| T19 | research_snapshot_20261123.json series_store | JP_CPI_YOY@2026-02 | 1.27 | 1.27 | 辅助(不计入) |
| A41 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-11-20 星期 | Friday | Friday | 辅助(不计入) |
| A42 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-11-23 星期 | Monday | Monday | 辅助(不计入) |
| A43 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-08-23 星期 | Sunday | Sunday | 辅助(不计入) |
| C07 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2027-02-28 合法日期/星期 | Sunday | Sunday | 辅助(不计入) |
| C09 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-11-23→2027-02-28 天数 | 97 | 97 | 辅助(不计入) |
| K01 | report.json agent_judgment.contract_verification.stats | checks | 17 | 17 | 辅助(不计入) |
| K02 | report.json agent_judgment.contract_verification.stats | verified | 15 | 15 | 辅助(不计入) |
| K03 | report.json agent_judgment.contract_verification.stats | contradicted | 0 | 0 | 辅助(不计入) |
| Q05 | research_snapshot_20261123.json gate_a.core_fail | core_fail 项数 | 0 | 0 | 辅助(不计入) |
| Q06 | research_snapshot_20261123.json gate_a.noncore_fail | noncore_fail 项数 | 0 | 0 | 辅助(不计入) |
| U_wd_2026-11-05 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-05 星期 | Thursday | Thursday | 辅助(不计入) |
| U_wd_2026-11-09 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-09 星期 | Monday | Monday | 辅助(不计入) |
| U_wd_2026-11-13 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-13 星期 | Friday | Friday | 辅助(不计入) |
| U_wd_2026-11-14 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-14 星期 | Saturday | Saturday | 辅助(不计入) |
| U_wd_2026-11-15 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-15 星期 | Sunday | Sunday | 辅助(不计入) |
| U_wd_2026-11-20 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-20 星期 | Friday | Friday | 辅助(不计入) |
| X01 | MAP_REPORT.md(引擎渲染面)『TIPS_10Y 引擎当前面: 近30日 2.66→2.88, 上升22bp』× snapshot.series_store.TIPS_10Y | 渲染面『近30日』窗 2026-10-23→2026-11-19 实际利率变动(bp) | 22.0 | 22.0 | 辅助(不计入) |
| X02 | research_snapshot_20261123.json series_store.TIPS_10Y@2026-10-23 | 渲染面所引窗起值 2.66 | 2.66 | 2.66 | 辅助(不计入) |
| X03 | MAP_REPORT.md | 渲染面确含『近30日2.66→2.88,上升22bp』字样 | True | True | 辅助(不计入) |
| X16 | report.json run_ok / steps[*].ok / steps[S8_grounded_qa].envelope | run_ok=true 且 66 步 step 级 ok 全为 true(62 已执行+4 未执行); S8_grounded_qa 信封含 unmapped(地图问句不属其支持的问题类型, 非失败步骤) | True | True | 辅助(不计入) |
| X17 | research_snapshot_20261123.json series_store.UST_10Y/TIPS_10Y/BEI_10Y | 10-23→11-19 窗三利率恒等残差=0(+4 = +22 − 18) | True | True | 辅助(不计入) |
| X51 | AGENT_SEAT_ENVELOPE.json | frozen_inputs 三项 sha256 前16位与实测文件一致(完整性前提; 受审稿无对应文字) | True | True | 辅助(不计入) |

## 5 首轮检查口径修正记录

本席首轮检查中有 13 组 19 点因检查设计不当报出「偏离」; 经定位均为检查口径问题而非受审稿错误, 已按下列方式重述, 清单以重述后的口径为准。逐条如实列出以备复核。

| 点 | 首轮检查 | 定位 | 重述后口径 | 结果 |
|---|---|---|---|---|
| P18/P20 | DFF 锚值与最新值的观测日按「观测日 ≤ 锚日/截止日」朴素选取 | 引擎锚格按发布纪律选取(DFF 发布=观测日+1 天) | 改为「发布日 ≤ 锚日/截止日」的最新观测 | 一致 |
| P71 | 日历条目存在性检查误匹配美国数据发布类条目 | 受审稿所指为美国政策/FOMC 类条目 | 按条目类别只筛政策类条目 | 一致 |
| I30 | 以序列月首观测日 2026-10-01 比对「观测 2026-10」 | 受审稿与证据索引以期间末 2026-10-31 标注且已披露两口径 | 同一观测的两种标注并列核对 | 一致 |
| T18 | 候选面 value_before 与序列值比对时取错字段(value_after) | 检查取错字段 | 改取对应字段, 以两面残差计 | 一致(残差 0.0) |
| V01/V02 | 锚格按「观测日 ≤ 锚日」重选 | 同 P18/P20 | 按发布规则重选 | 35 格与 35 项全部一致 |
| U34 | 发布依据措辞逐字比对(「实录锚」/「实测锚」) | 受审稿为转述 | 按语义核对 | 一致 |
| A01/A17 | 水平值按 4 位小数比对 float32 展开值 | 精度位设定不当 | 改 6 位小数 | 一致 |
| A31 | 引擎窗美日股指跌幅落差按带符号差比对 | 受审稿载绝对差 | 取绝对值 | 一致 |
| A40 | 预设汇率两端值属共同交易日窗 | 所引为引擎月窗两端值 | 改按引擎月窗核对; 另立 A44/A45 验三窗方向 | 一致 |
| T04 | 0.3767 按 4 位小数比对未舍入差 | 受审稿取所引四位小数之差 | 按所引四位值之差; 另立 T04b 对引擎候选面 delta | 一致 |
| X16 | 以 step 级 ok=False 判失败步 | 66 步 step 级 ok 全为 true; 「ok False」系 S8 信封状态 unmapped | 重述为步骤面事实 | 一致 |
| X21–X24 | 锚格观测日取 2026-08-01 | 月频序列月首日, 且 2026-08 观测发布晚于锚日 | 按发布规则得 2026-07-01 | 一致 |
| X33 | 证据索引行种类全按 snapshot_fact | 实为 44 行 snapshot_fact + 25 行 s3_envelope | 重述并核对 S3 信封源快照 | 一致 |

方法修正一处: 首轮数字覆盖复扫以 \w 作 token 边界, 漏掉紧贴字母/汉字的数字(如 -8bp、18格); 本轮改用 ASCII 边界复扫并对计数类数字(数字+量词)单独清点, 新增比对点 X47–X50(点值格 18 格、缺席 4 格、+67bp、36 个月史), 均一致。

## 6 六查逐项结论

六查 = 证据相关性 / 支持度 / 竞争解释(是否真正竞争) / 反对证据 / 结论是否超出证据 / 证伪条件可观测性。

### 6.1 C1-POLICY-DIVERGENCE($.l3.contradictions[0])

受审陈述要旨: 政策维是可比口径下方向最清晰的分化——美国与日本同向收紧、中国在可比口径上未变; 美国上限 3.75→4(上调 25bp), 引擎事件簇 2026-09-16 决议、2026-09-17 生效(决议日系推定); 美日决议相隔两日、同一周内同步收紧, 不据此排序; 「中国未变」仅就 LPR 与七天逆回购成立; 欧元区政策序列缺席不纳入。

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | 引用 DFEDTARU@2026-11-23、DFF@2026-11-19、JP_POLICY_RATE@2026-10-01、CN_LPR_1Y@2026-11-20 均属政策维; 冻结日历载日本央行目标条目(决议 2026-09-18、生效 2026-09-24、目标 1.25)与维持条目(2026-10-30); 日历无美国政策/FOMC 条目, 与「美国决议日系引擎推定」一致(P71) |
| 支持度 | 通过(P01–P72 逐项一致) | DFEDTARU 3.75→4.0(生效 2026-09-17, +25bp; 决议日=生效日前一日, P06/P10), 近一年先降后升净 0(P17); DFF 3.63(2026-08-22)→3.88(2026-11-19); JP_POLICY_RATE 0.978(2026-07)→1.227(2026-10), 台阶 0.977/1.043/1.227(P28–P30), 12 个月窗六个变动点 [8,17,11,14,7,18] 合计 +75bp(P34/X37); CN_LPR_1Y 四期均 3.0(P50); CN_OMO_7D 1.4→1.4(末次 2026-10-30, P57/P58); CN_POLICY_OVERNIGHT 1.25(2026-11-23)、锚前无观测(P62); 两决议日相隔 2 日且同属 ISO 周第 38 周(P43/P44) |
| 竞争解释 | 真正竞争, 非稻草人 | 解释一(同一全球冲击: 能源价格/通胀预期, 推论「后续美日应继续同步」)与解释二(各自独立: 美国通胀读数触发、日本正常化节奏; 中国不变响应内需)对「美日同步」成因相反; 受审稿以决议日油价对账后明确写「不足以区分两解释」, 未偏袒任一方 |
| 反对证据 | 未见与陈述相左的数据; 边界均已披露 | ① 美国决议日为推定——偏移 ±2 日仍在同一周, 「同一周内同步收紧」稳健; ② 七天逆回购末观测过期(滞后 24 天>10 天窗, X19), 受审稿写明; ③ 隔夜利率 2026-11-02 换锚后无锚前观测, 受审稿写明并声明该口径对照不可得; ④ 日本方向由市场利率逐月上行至目标 1.25 佐证(日历条目本身只载目标水平); ⑤ 能源价格 11 月回落见 MINOR-1 |
| 结论是否超出证据 | 未超出 | 「方向最清晰的分化」「同向收紧」「可比口径未变」均有数值支撑; 未作因果先后排序; 欧元区明确不纳入对照 |
| 证伪条件可观测性 | 通过(附一条 NIT) | 陈述层为事实对照, 无需证伪条件; 解释一有可观测推论, 解释二缺可观测判据(NIT-5) |

### 6.2 C2-INFLATION-DIVERGENCE($.l3.contradictions[1])

受审陈述要旨: 三个月对照窗内三地通胀读数均高于三个月前, 分化在水平不在方向; 日本 1.97→2.44、东京都 1.85→2.73; 美国 CPI 水平 337.476, 最新月同比因缺上年同月基期不可得, 最近有效 3.72(2026-09)高于 3.30; 核心 CPI 水平 339.9, 最近有效同比 2.57 高于 2.47; 核心 PCE 水平 130.902, 同比 3.04→3.12; 中国 CPI 0.5→0.7、PPI 3.5→5.7; 转折面的「美日方向分化」取另一组窗口。

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | 引用 JP_CPI_YOY/CPI/CORE_CPI/CORE_PCE/CN_CPI_YOY/CN_PPI_YOY 均属通胀维, 且各载发布日与发布依据 |
| 支持度 | 通过(I01–I36、I30b 逐项一致) | 各锚值与最新值、发布日(2026-11-20、2026-10-30、2026-11-13、2026-10-30、2026-11-09)与推定规则吻合; 同比均以序列内上年同月观测直算(I13/I19/I23/I24); 基期缺席处(美国 2026-10 CPI 与核心 CPI, I12/I18)受审稿如实标「不可得」; 「三地均高于三个月前」逐项成立(I33–I36) |
| 竞争解释 | 真正竞争 | 解释一(进口成本传导→随基数消退回落)与解释二(服务与工资传导→持续偏高)给出相反的后续读数路径; 受审稿写明「本证据面无通胀分项数据，两解释不可区分」, 未虚构分项 |
| 反对证据 | 未见相左数据; 窗口依赖已披露 | 「美日方向分化」仅在转折窗口成立, 受审稿已声明窗口不同并给出起止(2026-05→2026-08 与 2026-06→2026-09)及其与对照窗的关系 |
| 结论是否超出证据 | 未超出 | 结论限定为「分化体现在水平」「方向上未见经济体之间的反向」; 美国通胀是否转向在转折叙述中明写「证据不足」 |
| 证伪条件可观测性 | 通过 | 两解释各附可观测的后续读数路径 |

### 6.3 C3-GROWTH-LIMITED($.l3.contradictions[2])

受审陈述要旨: 增长维以状态延续为主, 仅小幅方向差异; 美国 GDP 同比 2.19→2.07、失业率 4.1→4.1、工业生产同比 1.25→2.15、中国 PMI 49.2→49.3(两期均在荣枯线下方)、日本 GDP 同比 0.80→1.16; 分化证据不足以单独成论。

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | 引用 US_REAL_GDP/UNEMPLOYMENT/INDPRO/CN_PMI_MFG 均属增长维; 日本 GDP 同比标明「不在本轮证据索引，按降级口径引用」 |
| 支持度 | 通过(G01–G19 逐项一致) | GDP 水平 24611.077 与同比 2.07/2.19(G03/G04)、失业率 4.1/4.1(G06/G07)、工业生产同比 2.15/1.25(G11/G12)、PMI 49.3/49.2(G14/G15)、日本 GDP 同比 1.16/0.80(G16/G17); 发布日 2026-10-29/2026-11-05/2026-11-15/2026-10-30/2026-11-14/2026-08-14 与推定规则吻合 |
| 竞争解释 | 真正竞争 | 解释一(制造业回暖 vs 出口地产拖累→美中分化并传导)与解释二(季节性与单月波动→大体延续)相反, 且各以可核对的幅度为据 |
| 反对证据 | 未见相左数据; 版本口径已披露 | 变动幅度: GDP 同比 -0.12 个百分点、工业生产同比 +0.90 个百分点、失业率 0、PMI +0.1、日本 GDP 同比 +0.36 个百分点; GDP 取最新修订值, 受审稿标「事后回顾口径，非当时首发值」 |
| 结论是否超出证据 | 未超出(取保守一侧) | 结论为「证据不足以单独成论」, 未把小幅差异写成分化 |
| 证伪条件可观测性 | 通过 | 解释一含可观测推论(增长维美中分化并传导至通胀与政策) |

### 6.4 C4-EVIDENCE-BOUNDARY($.l3.contradictions[3])

受审陈述要旨: 欧元区三维序列全部缺席; 资产两口径并列; 引擎窗下 SPX -5.51% 与 NIKKEI225 -9.98% 相差 4.47 个百分点并不相近, SPX 与 SHCOMP 落差 1.40 个百分点; 跌幅差属推断; 以四地为主语的横向分化结论均证据不足; 另两项口径不可得。

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | DAX/SPX/NIKKEI225/SHCOMP/VIX 均属资产面且与资产月窗引擎面同窗; 欧元区缺席由 series_store、sources_status.ea 与 Gate A 非核心缺口三面互证(P63–P68, Q03/Q13) |
| 支持度 | 通过(A01–A45 逐项一致) | 引擎窗 SPX -5.51%、NIKKEI225 -9.98%、SHCOMP -4.11%、DAX +0.11%、VIX +38.87%; 收盘窗 -9.36%/-9.98%/-4.25%/-1.50%/+84.52%; 落差 4.47 与 1.40 个百分点(A31); 盘中反弹 SPX +4.25%、VIX -24.74%; DAX 25209.45(2026-11-23 盘中) |
| 竞争解释 | 真正竞争 | 解释一(宏观预期分化→后续数据与跌幅排序同向)与解释二(估值与仓位→跌幅差收敛)均可观测 |
| 反对证据 | 窗口敏感性已由受审稿自行披露 | 两口径下美日跌幅「相近/不相近」相反, 受审稿并列披露并拒绝把跌幅差外推为宏观分化; 11-23 为盘中快照已标注 |
| 结论是否超出证据 | 未超出 | 「证据不足」为保守结论; 两项不可得口径属实(美国 2026-10 CPI 同比缺基期; 隔夜利率序列自 2026-11-02 起) |
| 证伪条件可观测性 | 通过 | 两解释各附可观测推论 |

### 6.5 M1-POLICY-RATES-ASSETS($.l3.mechanism_chains[0])

受审链条要旨: 环 1 观察(E1)政策对照; 环 2 传导【假设】长端利率分解(近一月共同交易日窗 名义 -8bp=实际 +11bp+盈亏平衡 -19bp; 12 个月窗 +91bp=+102bp−11bp; 残差均 0); 环 3 资产面【假设】两口径资产变动。

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | 环 1 政策序列; 环 2 TIPS_10Y/BEI_10Y/UST_10Y; 环 3 股指与 VIX; 各环区分指标与主张对应 |
| 支持度 | 通过(数值逐项一致) | 环 1 同 C1; 环 2 两窗分解与引擎面 us_rates_trio 同值, 恒等残差均 0(R 组 24 点; 残差 R08/R12); 环 3 同资产点 |
| 竞争解释 | 真正竞争 | 环 2 竞争解释(通胀预期与仓位渠道)、环 3 竞争解释(仓位与流动性)均与主解释预期相反, 并给出区分指标与两侧预期 |
| 反对证据 | 有, 且受审稿已如实纳入 | ① 12 个月窗美国政策净 0 而实际利率 +102bp——受审稿自己写明「政策净变动为零时实际利率的上行不由政策变动解释」并把该环定为【假设】; ② 引擎窗下美日跌幅不相近, 单一传导弱化; ③ 盈亏平衡仅覆盖美国国债市场; ④ 近一月窗口径与渲染面「近30日」窗未对账(MINOR-3) |
| 结论是否超出证据 | 未超出 | 环 2/环 3 均标【假设】, 传导裁定三环均「尚不能区分」, 未把恒等式当作因果 |
| 证伪条件可观测性 | 通过 | 区分指标 TIPS_10Y、BEI_10Y、VIX 均为在库日频序列, 主/竞争两侧预期均写成可观测形态 |

### 6.6 M2-CN-PPI-CPI-SCISSORS($.l3.mechanism_chains[1])

受审链条要旨: 环 1 观察: PPI 3.5→5.7、CPI 0.5→0.7(发布 2026-08-09→2026-11-09)、LPR 3→3、PMI 49.2→49.3; 环 2 传导【假设】: 剪刀差挤压下游利润/若传导则政策空间收窄; 区分指标 CN_CPI_YOY 相对 CN_PPI_YOY, 时限至 2027-02-23; 剪刀差由 3.0 扩至 5.0 个百分点, 尚无传导迹象。

| 查项 | 结论 | 依据 |
|---|---|---|
| 证据相关性 | 通过 | CN_PPI_YOY/CN_CPI_YOY/CN_LPR_1Y/CN_PMI_MFG 与各环主张对应 |
| 支持度 | 通过 | 剪刀差 (3.5−0.5)=3.0 与 (5.7−0.7)=5.0 个百分点; 发布日按月末+9 天推定(2026-08-09、2026-11-09)吻合, 受审稿标「引擎推定规则，非日历实录」; LPR 与 PMI 同 C1/C3 |
| 竞争解释 | 两分支互斥且可区分 | 挤压分支(PPI 高位、CPI 低位延续)与传导分支(CPI 随 PPI 上行)给出相反的后续走势 |
| 反对证据 | 「尚无传导迹象」经反方检验可成立 | 2026-07 至 2026-10 中国 PPI 3.5→3.8→5.0→5.7、CPI 0.5→0.8→0.9→0.7: CPI 未随 PPI 稳定同向, 2026-10 PPI 升而 CPI 回落 |
| 结论是否超出证据 | 未超出 | 可核环节仅剪刀差读数; 传导环标【假设】并写明缺环 |
| 证伪条件可观测性 | 通过 | 2027-02-23=截止日+3 个月(C08); 区分量为两条在库月频序列的相对走势, 两侧预期互斥 |

### 6.7 传导面(reader_map.transmission, 三环)与同步面

- 环 1(实际利率渠道): 观察面数值全部一致(政策对照、TIPS_10Y +11/+102bp、最新 2.88、名义 5.04/−8bp、政策窗内净 0); 主/竞争两侧预期均写成可观测形态; 裁定「尚不能区分」有据(两窗方向合主解释, 政策净变动与实际利率上行不同步合竞争解释)。
- 环 2(通胀预期渠道): BEI_10Y −19/−11bp、窗末 2.16、最新 2.15 一致; 裁定「尚不能区分」有据(回落与竞争解释的字面预期相左, 但受审稿承认「政策可信」读法可相容, 并声明指标只覆盖美国国债市场)。
- 环 3(仓位与流动性): 数值一致(含 CAC40 +1.86%、DAX +1.64%); 收盘窗合主解释、引擎窗与盘中反弹合竞争解释, 裁定「尚不能区分」有据。
- 同步面: 三环 face_off_verdict 均为「尚不能区分」, MAP_REPORT 渲染「尚不能区分」5 处(X07), verdict_note 正文未进入渲染面; 受审稿注记⑤「读者所见裁定为 face_off_verdict 标签」属实, 叙述与引擎同步面无冲突。

### 6.8 转折面(reader_map.turnings ×3 与 turning_supplement)

- 三个转折窗口与引擎候选池 turning_candidates_top9 一致(T16/T17): ① JP_POLICY_RATE 2026-04 0.727→2026-07 0.978(+0.251 个百分点); ② JP_CPI_TOKYO_YOY 2026-06 1.6→2026-09 2.69(+1.09 个百分点), 其后 2026-10 为 2.73; ③ CORE_CPI 2026-05 2.8229→2026-08 2.4462(回落 0.3767 个百分点, 见 NIT-1), 其后 2026-09 为 2.5658。
- 窗口终点与锚的关系披露属实: ①终点 2026-07 早于锚(2026-08-23); ②终点 2026-09 落在对照窗之内; ③终点 2026-08 早于锚; 其余通胀候选窗口终点均在 2026-05 或之前(T20)。
- ①③ 被引擎并项、补选美国工业生产(2025-11→2026-02): 与引擎并项/补选规则文本及 MAP_REPORT「引擎补选」字样一致(X15); 补选项数值 1.7543→0.7972(−0.9571 个百分点)、相邻窗对照 2.434→4.1666 与 −2.3904→1.0101(PMI 49.0→50.0)一致。
- 叙述与引擎同步面无冲突。

### 6.9 情景面($.l4.scenarios ×2)

- 阈值派生: 4.25=4.0+0.25; 1.28=1.23(1.227 取两位)+0.05; 2.90=3.0−0.10(C01–C03); 截止日取值 4.0/1.227/3.0 均未触发(C04–C06); 期限 2027-02-28 为合法日期(C07); 两情景触发条件互斥(K17); 均标「假设·非预测」。
- 证伪条件与触发条件互补且可观测: DFEDTARU 为日频在库序列; JP_POLICY_RATE 月均按月末+5 天推定发布(2027-01 月均于 2027-02-05 前可见), 期限前可取; CN_LPR_1Y 每月 20 日 09:00 发布(日历 RC-CN-LPR-2026M11)。
- 资产方向: SCN-A 所引数值与引擎月窗一致(MINOR-2 仅涉「同窗」所指); SCN-B 明确写「与近一月观察相反，属并列反例情景」。
- 瑕疵: SCN-B 叙述句与触发行在「美国降息且中国下调」组合下不一致(MINOR-4); 「互补而不穷尽」措辞(NIT-2)。

### 6.10 历史段同步性

- history_periods 为空(零段); 契约允许 0..3 段且要求零段注记(X39), 零段注记在场。
- 零段注记所载数值与引擎 S6 类比面逐项一致(N01–N28, X08/X09, X50): 扫描 1871、有效 74、特征不足 1785、同簇去重 12、TOP-5 及排序依据、覆盖率与贡献份额、锚点月缺席特征 12 项及原因(含 36 个月史)、模式门(描述性可用/事件研究阻断)。
- 叙述称「类比面特征与事后窗全部为美国序列」与引擎面(事后表现 SPX/UST_10Y/DXY/GOLD_F, 美国序列锚定)一致; 叙述未引用引擎同步面之外的历史数字; 明示「事后结果≠当时可知」, 未以事后结果冒充当时可知。
- 结论: 叙述与引擎同步面无冲突, 不构成 REVISE 级问题。

### 6.11 披露与边界类陈述核对

- 引擎缺口披露①–⑥(X04–X06, X10–X12, I30/I30b, Q03/Q12, U35)与引擎面一致; 交付门陈述与 blocked_class_of 常量一致(X14: 核心维度缺数类属阻断); 日历版本 v1.5.0(X13); 证据索引 69 行(X33); 点值格 18 格+缺席 4 格(X47/X48); 候选池 9 取 3(T16); 信封历史段 0..3(X39); schema 1.1(X40); +75bp 与 +67bp 两个起算口径(P34, X37, X49)。
- 截止纪律: 受审稿全文晚于截止日的日期仅为情景期限(D01); 所用 34 条序列末观测日均不晚于截止日(D02)。

## 7 反方攻击记录

每条 L3 矛盾陈述与每条机制链至少一次; 另对传导环、转折、情景、历史同步面与锚格发布纪律各作攻击。

1. 反方攻击 1(C1 同步性): 美国决议日 2026-09-16 系引擎按「生效日前一日」推定, 冻结日历无美国政策条目——若实际决议日偏移, 「相隔两日」即失效 → 直算: 引擎事件簇决议 2026-09-16/生效 2026-09-17, 日本央行决议 2026-09-18 为日历实录, 两日相隔 2 天且同属 ISO 周第 38 周; 受审稿已标注推定并声明不据此排序先后, 「同一周内同步收紧」对 ±2 日偏移稳健 → 未推翻。
2. 反方攻击 2(C1「中国未变」): 七天逆回购末观测 2026-10-30 已过期(滞后 24 天>10 天窗), 隔夜利率 2026-11-02 换锚后无锚前观测——「未变」可能失真 → 直算: CN_LPR_1Y 四期均 3.0, CN_OMO_7D 2026-08-21 之后 34 个观测均 1.4, 隔夜最新 1.25(2026-11-23); 受审稿把「未变」限定于 LPR 与七天逆回购两口径并披露过期与换锚, 隔夜口径明写「三个月对照不可得」 → 未推翻(披露充分)。
3. 反方攻击 3(C1 日本方向): 冻结日历只载目标水平 1.25, 不载升/降方向 → 直算: 2026-08 月均 0.977 低于目标 1.25, 2026-09 月 1.043、2026-10 月 1.227 逐月上行逼近目标 → 方向为收紧, 未推翻。
4. 反方攻击 4(C1 能源竞争解释): 决议日 WTI_F 较锚高 17.65%/15.21% 既合「同一全球冲击」也合「各自独立」; 另核「11-09 起再度跌破该锚」 → 直算: 11-09 首次跌破(86.85<87.06)属实, 但 11-12=88.74、11-13=88.56 回到锚上方, 11 个观测中 9 个低于锚 → 受审稿对两解释如实写「不足以区分」(通过); 持续性表述不精确, 记 MINOR-1。
5. 反方攻击 5(C2 同比基期): 美国最新月同比是否以相邻基期冒充 → 直算: CPI/CORE_CPI 序列无 2025-10 观测, 2026-10 同比不可得; 受审稿如实标「不可得」并另列 2026-09 最近有效同比 3.72/2.57(以 2025-09 为基直算一致) → 未成立。
6. 反方攻击 6(C2 窗口选择): 「三地读数均高于三个月前」「美日方向分化」是否依赖窗口 → 直算: 对照窗内日本 1.97→2.44、东京都 1.85→2.73、美国 3.30→3.72、核心 2.47→2.57、核心 PCE 3.04→3.12、中国 CPI 0.5→0.7、PPI 3.5→5.7 逐项成立; 「美日方向分化」仅在转折窗口成立, 受审稿已声明两窗起止 → 未推翻(窗口依赖已披露)。
7. 反方攻击 7(C3 幅度与版本): 增长维变动是否足以称分化, 最新修订值是否冒充当时可知 → 直算: 变动幅度 GDP 同比 -0.12 个百分点、工业生产同比 +0.90 个百分点、失业率 0、PMI +0.1、日本 GDP 同比 +0.36 个百分点; 受审稿结论为「证据不足以单独成论」且 GDP 标「最新修订值，事后回顾口径，非当时首发值」 → 未推翻。
8. 反方攻击 8(C4 资产双窗): 引擎窗含 11-23 盘中快照, 收盘窗止于 11-20, 两窗下美日跌幅「相近/不相近」相反 → 直算: 引擎窗 SPX -5.51%/NIKKEI225 -9.98%(落差 4.47 个百分点), 收盘窗 -9.36%/-9.98%(相近), 11-23 盘中 SPX 较 11-20 收盘 +4.25%; 受审稿并列披露并拒绝把跌幅差外推为宏观分化 → 未推翻。
9. 反方攻击 9(C4 欧元区缺席): 欧元区是否确无可用宏观序列 → 直算: EA_REAL_GDP_YOY、EA_HICP_YOY、ECB_MRO、ECB_DFR、BUND_10Y、BUND_2Y 六项在 series_store 缺席, sources_status.ea=MISSING, Gate A 列为非核心缺口 → 未推翻。
10. 反方攻击 10(M1 政策→利率因果): 12 个月窗美国政策先降后升净 0 而实际利率 +102bp, 因果环不成立 → 直算: 两窗恒等残差均为 0, 政策净 0; 受审稿自己指出「政策净变动为零时实际利率的上行不由政策变动解释」, 环 2 标【假设】, 传导裁「尚不能区分」 → 攻击被受审稿吸收, 未推翻。
11. 反方攻击 11(M1 窗口径): 改用渲染面「近30日」窗(2026-10-23→2026-11-19) → 直算: 名义 +4bp=实际 +22bp+盈亏平衡 -18bp(残差 0), 与受审稿 10-20→11-19 窗(名义 -8bp=实际 +11bp+盈亏平衡 -19bp)并存; 「盈亏平衡降幅大于实际上行幅度」仅在后一窗成立, 两窗方向结论一致 → 记 MINOR-3(未对账披露), 结论未推翻。
12. 反方攻击 12(M1 汇率「同窗」): 若「同窗」指共同交易日窗, USDJPY 应为 +0.54% 而非 +1.82% → 直算: 所引两端值 156.494/159.347 为 2026-10-23/2026-11-23 观测(引擎月窗 +1.82%), 共同交易日窗 +0.54%(158.523→159.381), USDCNY 引擎月窗 -0.35%、共同交易日窗 -0.35%(两位小数下同为 -0.35%); 数值正确、三窗方向一致 → 记 MINOR-2(所指不明), 结论未推翻。
13. 反方攻击 13(M2 传导迹象): 中国 CPI 2026-08/09 曾升至 0.8/0.9, 是否已是传导迹象 → 直算: 2026-07 至 2026-10 中国 PPI 3.5→3.8→5.0→5.7、CPI 0.5→0.8→0.9→0.7; CPI 未随 PPI 稳定同向, 2026-10 PPI 升而 CPI 回落 → 「尚无传导迹象」可成立, 未推翻。
14. 反方攻击 14(转折并项/补选): 受审稿称①③被引擎并项并补选美国工业生产, 是否属实; 窗口终点是否越出对照窗 → 直算: 候选池 9 项与信封 turning_candidates_top9 一致(T16/T17), 引擎规则「同维度且观测窗重叠=同一轮」且 MAP_REPORT 载「引擎补选」(X15), 补选项 1.7543→0.7972(-0.9571 个百分点)一致; 窗口终点与锚的关系披露属实 → 未推翻。
15. 反方攻击 15(情景阈值与互斥): 阈值是否可派生、可观测, 两情景是否互斥, 叙述与触发条件是否一致 → 直算: 4.25=4.0+0.25、1.28=1.23+0.05、2.90=3.0-0.10, 截止日取值 4.0/1.227/3.0 均未触发, 两情景触发条件互斥; 但 SCN-B 叙述句「美国转向降息不属本情景」与触发行「上限 ≤4」在「美国降息且中国下调」组合下不一致 → 记 MINOR-4, 阈值本身未推翻。
16. 反方攻击 16(期限可观测性): 2027-02-28 前能否取到「期限前已发布的最新月均」 → 直算: 期限为合法日期, JP_POLICY_RATE 月均按月末+5 天推定发布(2027-01 月均于 2027-02-05 前可见), DFEDTARU 日频、LPR 每月 20 日 09:00 发布 → 可观测, 未推翻。
17. 反方攻击 17(历史同步面): 零段注记所载数字是否与引擎类比面冲突, 是否以事后结果充数 → 直算: 扫描 1871/有效 74/特征不足 1785/去重 12、TOP-5、覆盖率与贡献份额、缺席特征 12 项及原因(含 36 个月史)全部一致; 契约允许 0..3 段 → 无同步性冲突, 未推翻。
18. 反方攻击 18(锚格发布纪律): 锚值是否取到发布晚于锚日的观测, 是否有晚于截止日的发布混入 → 直算: 35 个锚格按发布规则独立重选逐位一致(V01), 35 项 anchor_echo 一致(V02), 受审稿全文晚于截止日的日期仅情景期限(D01), 所用 34 条序列末观测日均不晚于截止日(D02) → 未推翻。

## 8 问题清单

### MAJOR(0 条)

无。§5 六项 MAJOR 判据逐项核对: 数字/日期/方向错或与证据相左——唯一偏离 E25 的首次跌破日期正确、持续性表述不精确, 定 MINOR; 缺基期却给出同比——无(美国 2026-10 同比如实标缺); 以相邻口径冒充——无(盘中/收盘、月均/宣布目标、观测日/期间末逐处标注); 事后信息冒充当时可知——无(GDP 等标「事后回顾口径」, 全部发布日不晚于截止日); 结论超出证据且无标注——无; 证伪条件不可观测——无。

### MINOR(4 条, 不阻断)

1. **agent_judgment.json quality_gate_notes[0](证据与口径·能源价格对账) — $.quality_gate_notes[0]**
   - 问题: 「11-09 起再度跌破该锚」: 首次跌破日属实(WTI_F 2026-11-09=86.85<锚 87.06), 但持续性表述与序列相左——11-12=88.74、11-13=88.56 回到锚上方, 11-09 至 11-23 共 11 个观测中 9 个低于锚, 11-16 起才持续低于; 不改变「11 月油价回落至锚下」的对账结论(本席唯一偏离点 E25)
   - 原句: 「期货 9 月初至 10 月底的观测全部高于三个月前锚，11-09 起再度跌破该锚(8 月底曾短暂低于该锚)」
   - 建议改句: 「期货 9 月初至 10 月底的观测全部高于三个月前锚，11-09 首次再度跌破该锚(11-12、11-13 两个观测回到锚上方，11-16 起持续低于；8 月底曾短暂低于该锚)」
2. **agent_judgment.json l4.scenarios[0](SCN-A)·rows.asset_direction.direction — $.l4.scenarios[0].rows.asset_direction.direction**
   - 问题: 「同窗」所指不明: 同一括号内并列共同交易日窗(2026-10-20→2026-11-19)与引擎月窗两项, 所引 USDJPY 156.494→159.347(+1.82%)、USDCNY 6.6779→6.6542(-0.35%)为引擎月窗 2026-10-23→2026-11-23 两端观测, 数值正确; 若读作共同交易日窗则 USDJPY 为 +0.54%(158.523→159.381)、USDCNY 为 -0.35%; 三窗方向一致(美元对日元走强、对人民币未走强), 结论不变
   - 原句: 「同窗 USDJPY 156.494→159.347 为 +1.82%；对人民币并未走强: 同窗 USDCNY 6.6779→6.6542 为 -0.35%」
   - 另涉原句: 「单月窗名义 -8bp、盈亏平衡降幅大于实际上行幅度」
   - 建议改句: 「引擎月窗(2026-10-23→2026-11-23) USDJPY 156.494→159.347 为 +1.82%；对人民币并未走强: 同窗 USDCNY 6.6779→6.6542 为 -0.35%(共同交易日窗 2026-10-20→2026-11-19 下分别为 +0.54%、-0.35%，方向一致)」
3. **agent_judgment.json l3.mechanism_chains[0](M1)·links[1].text 与 reader_map.transmission[0].links[0].verdict_note — $.l3.mechanism_chains[0].links[1].text; $.reader_map.transmission[0].links[0].verdict_note**
   - 问题: 近一月利率窗两口径未对账: 受审稿取共同交易日窗 2026-10-20→2026-11-19(名义 -8bp=实际 +11bp+盈亏平衡 -19bp, 复算一致, 与引擎面 us_rates_trio 同值), 而同一研判档的渲染面 MAP_REPORT.md 载引擎『近30日』窗 2026-10-23→2026-11-19 为 TIPS_10Y 2.66→2.88 上升 22bp(直算: 名义 +4bp=实际 +22bp+盈亏平衡 -18bp, 残差 0); 「单月窗…盈亏平衡降幅大于实际上行幅度」仅在前一窗成立, 后一窗实际利率上行幅度大于盈亏平衡降幅; 两窗方向结论一致(实际利率为上行分量、盈亏平衡回落), 「尚不能区分」裁定不变
   - 原句: 「近一月共同交易日窗(2026-10-20→2026-11-19)名义 -8bp=实际利率(TIPS_10Y)+11bp+盈亏平衡(BEI_10Y)-19bp」
   - 建议改句: 「近一月共同交易日窗(2026-10-20→2026-11-19)名义 -8bp=实际利率(TIPS_10Y)+11bp+盈亏平衡(BEI_10Y)-19bp(引擎渲染面『近30日』窗自 2026-10-23 起算: 名义 +4bp=实际 +22bp+盈亏平衡 -18bp; 两窗方向一致，窗起不同致幅度不同)」
4. **agent_judgment.json l4.scenarios[1](SCN-B)·rows.scenario、l4.scenarios[0](SCN-A)·rows.scenario 与 quality_gate_notes[2] — $.l4.scenarios[1].rows.scenario; $.quality_gate_notes[2]; $.l4.scenarios[0].rows.scenario**
   - 问题: 情景 B 叙述句与触发行不一致: 触发行只要求「DFEDTARU 上限 ≤4」(含美国降息), 叙述句却称「美国转向降息…不属于本情景的收敛形态」; 证伪面注记「美国转向降息使延续情景失效而不触发收敛情景」仅在「中国未同步下调」时成立——若美国降息的同时 CN_LPR_1Y 下调至 2.90 或以下且日本月均低于 1.28, 按触发行应归入收敛情景。属情景定义的表述口径不一致, 不涉及证据面数字
   - 原句: 「美国转向降息(上限回落至 3.75 以下)不属于本情景的收敛形态」
   - 另涉原句: 「美国转向降息使延续情景失效而不触发收敛情景」
   - 另涉原句: 「美日不再加码而中国未变的平台态，以及美国转向降息，均不属任一情景」
   - 建议改句: 「美国转向降息而中国未下调时不属任一情景；若美国降息的同时 CN_LPR_1Y 下调至 2.90 或以下且 JP_POLICY_RATE 月均低于 1.28，则按触发行(DFEDTARU 上限 ≤4)归入本情景」

### NIT(5 条)

1. **agent_judgment.json reader_map.turnings[2].first_mover — $.reader_map.turnings[2].first_mover**
   - 说明: 「三个月回落 0.3767 个百分点」为所引四位小数之差(2.4462−2.8229), 与引擎候选面 delta 一致; 未舍入差为 0.376779(四舍五入 0.3768), 属末位舍入口径, 不改变方向与量级
   - 原句: 「三个月回落 0.3767 个百分点」
   - 建议: 「三个月回落约 0.377 个百分点(所引四位小数之差为 0.3767)」
2. **agent_judgment.json l4.scenarios[0..1].rows.scenario 与 quality_gate_notes[2] — $.l4.scenarios[0].rows.scenario; $.l4.scenarios[1].rows.scenario; $.quality_gate_notes[2]**
   - 说明: 「两情景互补而不穷尽」术语: 两情景的触发条件互斥而不穷尽, 「互补」仅就日本月均阈值 1.28 两侧与证伪面成立; 建议写「互斥而不穷尽」
   - 原句: 「两情景互补而不穷尽」
   - 建议: 「两情景互斥而不穷尽(日本月均阈值 1.28 两侧互补)」
3. **agent_judgment.json quality_gate_notes[3](数据面) — $.quality_gate_notes[3]**
   - 说明: 「本证据面为干净安装后的降级面(未接入历史补全流程)」属环境定性自述: 只读面(report.json、快照、工单信封)无对应字段——report.json 全文无「补全/backfill」字样, 仅 L2 注记载「干净 clone 常态」且 Gate A=DEGRADED; 「未接入历史补全流程」无法在证据面核验, 不影响任何结论; 建议注明来源(工单说明)或删去不可核的半句
   - 原句: 「本证据面为干净安装后的降级面(未接入历史补全流程)」
   - 建议: 「本证据面为降级安装面(Gate A=DEGRADED; 安装与历史补全流程状态依工单说明，引擎证据面不载)」
4. **agent_judgment.json quality_gate_notes[3](数据面) — $.quality_gate_notes[3]**
   - 说明: 「证据索引共 69 条，全部取自本工单冻结快照」: 69 行构成为 snapshot_fact 44 行 + s3_envelope 25 行(S3 概览/变动面行, 其信封源快照同为 research_snapshot_20261123), 来源表述成立但未写明构成
   - 原句: 「证据索引共 69 条，全部取自本工单冻结快照 research_snapshot_20261123」
   - 建议: 「证据索引共 69 条(snapshot_fact 44 行 + S3 概览/变动面行 25 行)，均取自本工单冻结快照 research_snapshot_20261123」
5. **agent_judgment.json l3.contradictions[0](C1)·competing_explanations[1] — $.l3.contradictions[0].competing_explanations[1]**
   - 说明: 竞争解释二的推论「同步只是巧合」未给出可与解释一相区别的可观测判据(解释一附有「后续美日应继续同步」的推论与能源价格对账面); 并列解释成立, 仅建议补一句可观测推论
   - 原句: 「则三地后续路径将按各自数据演变，同步只是巧合。」
   - 建议: 「则三地后续路径将按各自数据演变，同步只是巧合(可观测推论: 后续美日决议不再落于同一周或方向不一致)。」

### 已核对、不构成问题的观察项

1. 「交易所结算时刻属公开制度事实」: 外部制度事实, 受审稿已声明不来自引擎序列; 本席按规程不联网、只读面无制度日历, 未核验; 该句不承载数据结论(期货窗止于盘中快照的披露与快照面一致)。
2. 冻结日历日本央行目标条目与 FOMC 纪要条目的 source 记为验收指令(basis user_directive): 受审稿称「发布日历实录」系沿用引擎术语(日历条目优先于推定规则), 数值与条目一致。
3. 推定发布日落周末(2026-11-14 周六、2026-11-15 周日、2026-08-15 周六): 受审稿均标「引擎推定规则，非日历实录」, 与引擎面日期一致。
4. 能源对账的其余数值均一致: 9 月初至 10 月底 43 个观测全部高于锚(最低 88.28); 8 月底低于锚的观测为 08-24、08-25、08-26、08-27、08-28、08-31; 逐观测值: 11-09=86.85、11-10=86.04、11-11=86.53、11-12=88.74、11-13=88.56、11-16=85.72、11-17=86.01、11-18=83.26、11-19=83.21、11-20=83.98、11-23=82.02。
5. S8_grounded_qa 信封状态 unmapped: 地图问句不属该步支持的问题类型, 步骤面 ok, 非失败(X16 辅助)。
6. 「100% 归 Agent」: 席位归属声明, 非数据陈述。

## 9 裁决

**UPHELD**。MAJOR 0 条; 无 REVISE 级问题(历史段同步性无冲突, 结论均未超出证据)。比对点 403 点、偏离 1 点(E25)。MINOR 4 条与 NIT 5 条如实列于第 8 节, 均不改变受审稿任何结论, 不阻断。

## 10 边界自查与脚本清单

- 只读: 未修改运行目录与安装树内任何文件; 本席脚本与产出仅写于 /tmp/r32-accept/review6/C4_round1。
- 未联网; 未运行 ia_cli 的 plan/attach/report/archive/replay/update 等写操作; 未调用 agent_judgment.record_semantic_verdict。
- 未读取规程第 2 节禁止路径(research_archive/、树内 docs/、/tmp/r32-accept/out|scripts|replay|install*|final*、其他运行目录、其他 review 目录、~/investment-agent-product)。
- 未委派子代理; 未与研判席、操作者通信; 未索取、推测或依赖任何预审内容。
- 脚本(均在本席目录): rc_lib.py, s00_structure.py, s01_dump.py, s02a_policy_energy.py, s02b_macro.py, s02c_assets_rates.py, s02d_faces.py, s03_slices.py, s05_extra_checks.py, s06_merge_and_extra.py, s06_patch_restated_checks.py, s07_prep_index.py, s08_number_sweep.py, s09_inspect.py, s10_extra_points.py, s11_extra_points2.py, s12_dump_rest.py, s13_ctx.py, s14_count_sweep.py, s15_count_sweep2.py, s16_probe.py, s17a_data.py, s17b_text.py, s17c_probe.py, s17d_patch.py, s17e_patch.py, s17f_patch.py, s17g_check.py, s18_finalize.py
