# 一键研究报告(零模型编排 v2.0)
- 问题: 以 2026-08-21 为研究时点，日本和欧元区最近六个月的通胀与政策环境
- 运行: 20261124T080605Z @ cf33de3a9942578b71cecb45077b7a505d8fca01
- 快照: research_snapshot_20261121 (target 20260821)
- 数据门(gate_a): 39/39 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 欧元区(EA)、日本(JP) | 维度 通胀、货币政策 | 计划指标 6 项 | 对照点锚 6个月前@2026-02-21、最新一期@2026-08-21 | 事后偏移+(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 研究截止日(证据口径 r32): 2026-08-21 | 源快照 research_snapshot_20261121(版本日 2026-11-21) | 事实: 保留 1 / 重建 78 / 剔除 13+版本 0 | 序列剔观测 3743 | 版本不可得剔除 3 个观测 | 历史截止(晚观测/晚发布/当时不可得版本不入证据面)
  - 序列无可引用观测(已自证据面剔除): CN_POLICY_OVERNIGHT
  - 修订口径序列(无 as-of 版本快照): 只引用已过首个修订周期的观测,3 个观测=当时只见首发值而手头只有最新修订值,已剔除;引用值=最新修订版,不得表述为当时首发值: EA_HICP_YOY、EA_REAL_GDP_YOY、JP_CPI_YOY、JP_REAL_GDP_YOY、M2SL、SPX_CAPE、SPX_EPS、SPX_PE_TTM、US_REAL_GDP
- 研究时点口径: 问题声明研究时点 2026-08-21(显式时点标记)——截止日 2026-08-21
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖12 观测),缺口 2 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2026-02-21..2026-08-21)——任务窗窗口成员/覆盖不满足;任务窗2026-02-21..2026-08-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-06-17早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=1<65(日历期望130×半额;总量47不替代窗口归属)(问题未限定范围→daily频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2026-02-21..2026-08-21)——任务窗窗口成员/覆盖不满足;任务窗2026-02-21..2026-08-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-06-17早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=1<65(日历期望130×半额;总量68不替代窗口归属)(问题未限定范围→daily频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 7641.160156 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:SPX@2026-08-20]
- NDX = 29213.160156 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:NDX@2026-08-20]
- RUT = 2992.429932 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:RUT@2026-08-20]
- DXY = 98.900002 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:DXY@2026-08-20]
- EURUSD = 1.167379 usd_per_eur @2026-08-20 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-08-20]
- GOLD_F = 4571.399902 usd_per_oz @2026-08-20 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-08-20]
- SILVER_F = 68.026001 usd_per_oz @2026-08-20 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-08-20]
- BRENT_F = 93.779999 usd_per_barrel @2026-08-20 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-08-20]
- VIX = 16.01 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:VIX@2026-08-20]
- DAX = 25983.039062 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:DAX@2026-08-20]
- CAC40 = 8453.089844 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:CAC40@2026-08-20]
- USDJPY = 158.276001 jpy_per_usd @2026-08-20 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-08-20]
- USDCNY = 6.7295 cny_per_usd @2026-08-20 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-08-20]
- HY_OAS = 2.75 percentage_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-08-20]
- BB_OAS = 1.63 percentage_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-08-20]
- B_OAS = 2.94 percentage_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-08-20]
- CCC_OAS = 10.35 percentage_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-08-20]
- IG_OAS = 0.82 percentage_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-08-20]
- UST_2Y = 4.19 percent @2026-08-20 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-08-20]
- UST_10Y = 4.69 percent @2026-08-20 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-08-20]
- BEI_10Y = 2.34 percent @2026-08-20 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-08-20]
- CURVE_2S10S = 0.5 percentage_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-08-20]
- UST_5Y = 4.39 percent @2026-08-20 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-08-20]
- SHCOMP = 3903.72 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-08-20]
- HSI = 25698.49 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-08-20]
- NIKKEI225 = 66216.79 index_point @2026-08-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-08-20]
- JP_CPI_YOY = 1.97 percent @2026-07-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-07-01]
- ECB_DFR = 2.25 percent @2026-06-17 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-06-17]
- ECB_MRO = 2.4 percent @2026-06-17 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-06-17]
- EA_HICP_YOY = 2.9 percent @2026-07-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-07-01]
- JP_POLICY_RATE = 0.978 percent @2026-07-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-07-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=False
> 零模型管线: 本层(矛盾综合/推断)须编排层 Agent 补作,attribution=ai_inferred——本管线绝不代写。补作纪律: 四层标注(事实/推断/假设/尚未验证)+并列竞争性解释(Skill 纪律4/第9步);机制链每环标 E1(引擎直接可验证)/E2(部分支持,缺环明写【假设】)/E3(纯叙事,须给证伪指标)(纪律15)

### L4 条件情景层 produced=False
> 条件推演五行(纪律16: 情景[明写假设非预测]/资产方向判断[方向+置信层级]/敏感变量[1-2 个引擎指标]/证伪指标[可观测阈值]/触发条件[可观测条件+时限];单一情景不得单独呈现,至少并列基准与反例)归编排层 Agent;不冒充预测——本管线绝不代写

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-07 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-01 | 0.29042 | 0.0 | rates 43.1%、inflation 40.1% |
| 2 | 2024-01 | 0.572955 | 24.6377 | rates 41.5%、valuation 29.5% |
| 3 | 2021-02 | 1.15128 | 44.9275 | rates 57.0%、volatility 17.0% |
| 4 | 2023-01 | 1.181708 | 49.2754 | rates 56.8%、inflation 24.1% |
| 5 | 2020-02 | 2.228766 | 97.1014 | volatility 65.1%、rates 19.0% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率
> **事后结果标注**: 候选月=事后筛得的相似结构(相似度用到候选月全窗口数据);候选月**之后**的经济与资产表现为事后结果(事后≠当时可知,事后≠预测)——引用须以「事后实际」措辞,不得表述为当时可知或对本次的预测(纪律17)。

## 日度相关(引擎确定性面·读者版)

- EA_HICP_YOY×ECB_MRO 日收益×日变化 pearson = 0.2565(n=44 对,共同窗 1999-01..2026-06;描述性统计≠因果)


## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_EA 
- [OK |语义✔] S3_overview_JP 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_EA_HICP_YOY 
- [OK |语义✔] S4_history_ECB_MRO 
- [OK |语义✔] S4_history_ECB_DFR 
- [OK |语义✔] S4_history_JP_CPI_YOY 
- [OK |语义✔] S4_history_JP_CPI_TOKYO_YOY 
- [OK |语义✔] S4_history_JP_POLICY_RATE 
- [OK |语义✔] S4_history_UST_10Y 
- [OK |语义✔] S4_history_TIPS_10Y 
- [OK |语义✔] S4_history_BEI_10Y 
- [OK |语义✔] S4_history_UST_2Y 
- [OK |语义✔] S4_history_UST_5Y 
- [OK |语义✔] S4_history_CURVE_2S10S 
- [OK |语义✔] S4_history_SPX 
- [OK |语义✔] S4_history_NDX 
- [OK |语义✔] S4_history_RUT 
- [OK |语义✔] S4_history_DAX 
- [OK |语义✔] S4_history_CAC40 
- [OK |语义✔] S4_history_NIKKEI225 
- [OK |语义✔] S4_history_HSI 
- [OK |语义✔] S4_history_SHCOMP 
- [OK |语义✔] S4_history_DXY 
- [OK |语义✔] S4_history_EURUSD 
- [OK |语义✔] S4_history_USDJPY 
- [OK |语义✔] S4_history_USDCNY 
- [OK |语义✔] S4_history_GOLD_F 
- [OK |语义✔] S4_history_SILVER_F 
- [OK |语义✔] S4_history_BRENT_F 
- [OK |语义✔] S4_history_HY_OAS 
- [OK |语义✔] S4_history_IG_OAS 
- [OK |语义✔] S4_history_BB_OAS 
- [OK |语义✔] S4_history_B_OAS 
- [OK |语义✔] S4_history_CCC_OAS 
- [OK |语义✔] S4_history_VIX 
- [OK |语义✔] S5_compare 命中 33 个指标,compare 仅取注册表序前 2(EA_HICP_YOY,ECB_MRO);其余 ECB_DFR,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(55 行)

- snapshot_fact:SPX@2026-08-20 → SPX
- snapshot_fact:NDX@2026-08-20 → NDX
- snapshot_fact:RUT@2026-08-20 → RUT
- snapshot_fact:DXY@2026-08-20 → DXY
- snapshot_fact:EURUSD@2026-08-20 → EURUSD
- snapshot_fact:GOLD_F@2026-08-20 → GOLD_F
- snapshot_fact:SILVER_F@2026-08-20 → SILVER_F
- snapshot_fact:BRENT_F@2026-08-20 → BRENT_F
- snapshot_fact:VIX@2026-08-20 → VIX
- snapshot_fact:DAX@2026-08-20 → DAX
- snapshot_fact:CAC40@2026-08-20 → CAC40
- snapshot_fact:USDJPY@2026-08-20 → USDJPY
- snapshot_fact:USDCNY@2026-08-20 → USDCNY
- snapshot_fact:HY_OAS@2026-08-20 → HY_OAS
- snapshot_fact:BB_OAS@2026-08-20 → BB_OAS
- snapshot_fact:B_OAS@2026-08-20 → B_OAS
- snapshot_fact:CCC_OAS@2026-08-20 → CCC_OAS
- snapshot_fact:IG_OAS@2026-08-20 → IG_OAS
- snapshot_fact:UST_2Y@2026-08-20 → UST_2Y
- snapshot_fact:UST_10Y@2026-08-20 → UST_10Y
- snapshot_fact:BEI_10Y@2026-08-20 → BEI_10Y
- snapshot_fact:CURVE_2S10S@2026-08-20 → CURVE_2S10S
- snapshot_fact:UST_5Y@2026-08-20 → UST_5Y
- snapshot_fact:SHCOMP@2026-08-20 → SHCOMP
- snapshot_fact:HSI@2026-08-20 → HSI
- snapshot_fact:NIKKEI225@2026-08-20 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-07-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-06-17 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-06-17 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-07-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-07-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-08-20 → SZCI
- s3_envelope:CHINEXT@2026-08-20 → CHINEXT
- s3_envelope:HSCEI@2026-08-20 → HSCEI
- s3_envelope:NVDA@2026-08-20 → NVDA
- s3_envelope:AAPL@2026-08-20 → AAPL
- s3_envelope:MSFT@2026-08-20 → MSFT
- s3_envelope:TLT@2026-08-20 → TLT
- s3_envelope:IEF@2026-08-20 → IEF
- s3_envelope:SHY@2026-08-20 → SHY
- s3_envelope:HYG@2026-08-20 → HYG
- s3_envelope:LQD@2026-08-20 → LQD
- s3_envelope:GBPUSD@2026-08-20 → GBPUSD
- s3_envelope:WTI_F@2026-08-20 → WTI_F
- s3_envelope:GLD@2026-08-20 → GLD
- s3_envelope:USO@2026-08-20 → USO
- s3_envelope:EEM@2026-08-20 → EEM
- s3_envelope:EZU@2026-08-20 → EZU
- s3_envelope:FEZ@2026-08-20 → FEZ
- s3_envelope:EWU@2026-08-20 → EWU
- s3_envelope:EWG@2026-08-20 → EWG
- s3_envelope:EWJ@2026-08-20 → EWJ
- s3_envelope:INDA@2026-08-20 → INDA
- s3_envelope:FXI@2026-08-20 → FXI
- s3_envelope:BTC@2026-08-20 → BTC

## 注记

- 序列无可引用观测(证据口径: 整条自证据面剔除——2026-08-21): CN_POLICY_OVERNIGHT
- 数据版本口径(证据口径③: 注册表声明最新修订口径且无 ≤研究截止 2026-08-21 的快照版本——只引用已过首个修订周期的观测,3 个未过首修周期观测=当时数据版本不可得已剔除;引用值=最新修订版,不得表述为当时首发值): EA_HICP_YOY、EA_REAL_GDP_YOY、JP_CPI_YOY、JP_REAL_GDP_YOY、M2SL、SPX_CAPE、SPX_EPS、SPX_PE_TTM、US_REAL_GDP
- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): ECB_MRO、ECB_DFR
