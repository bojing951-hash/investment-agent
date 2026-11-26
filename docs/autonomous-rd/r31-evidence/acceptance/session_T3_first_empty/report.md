# 一键研究报告(零模型编排 v2.0)
- 问题: 2026年11月,日本和欧元区的央行当前官方政策目标利率各处于什么水平?最近六个月有无已决议但尚未生效的调整?两地通胀同比最新读数相比去年同月如何?请给出具体数据和各数据的公布时间。
- 运行: 20261122T133320Z @ ca916cdca7b749282e498d8c8f0eac8bf43b7372
- 快照: research_snapshot_20261122_v2 (target 20261122)
- 数据门(gate_a): 5/5 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知

## 四层区分

### L1 事实层 available=True

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=False
> 零模型管线: 本层(矛盾综合/推断)须编排层 Agent 补作,attribution=ai_inferred——本管线绝不代写。补作纪律: 四层标注(事实/推断/假设/尚未验证)+并列竞争性解释(Skill 纪律4/第9步);机制链每环标 E1(引擎直接可验证)/E2(部分支持,缺环明写【假设】)/E3(纯叙事,须给证伪指标)(纪律15)

### L4 条件情景层 produced=False
> 条件推演五行(纪律16: 情景[明写假设非预测]/资产方向判断[方向+置信层级]/敏感变量[1-2 个引擎指标]/证伪指标[可观测阈值]/触发条件[可观测条件+时限];单一情景不得单独呈现,至少并列基准与反例)归编排层 Agent;不冒充预测——本管线绝不代写

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2022-06 | 0.937493 | 0.0 | rates 37.0%、volatility 30.8% |
| 2 | 2025-03 | 0.971202 | 1.3699 | volatility 67.6%、rates 22.8% |
| 3 | 2020-10 | 1.288514 | 28.7671 | rates 88.6%、valuation 5.3% |
| 4 | 2023-10 | 1.298078 | 32.8767 | volatility 73.7%、valuation 14.0% |
| 5 | 2019-10 | 1.694433 | 94.5205 | volatility 41.1%、rates 35.1% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率


## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_EA 
- [OK |语义✔] S3_overview_JP 
- [OK |语义✔] S3_changes 
- [SKIP|—] S4_history 问题未命中指标——零实体映射时如实跳过(不造数)
- [SKIP|—] S5_compare 命中指标不足 2 个,无可对齐自配对(如实跳过)
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate analog 锚点月窗门(compare 未产出对齐门——命中<2 或被拒)
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(46 行)

- s3_envelope:SPX@2026-11-20 → SPX
- s3_envelope:NDX@2026-11-20 → NDX
- s3_envelope:RUT@2026-11-20 → RUT
- s3_envelope:SHCOMP@2026-11-20 → SHCOMP
- s3_envelope:SZCI@2026-11-20 → SZCI
- s3_envelope:CHINEXT@2026-11-20 → CHINEXT
- s3_envelope:HSI@2026-11-20 → HSI
- s3_envelope:HSCEI@2026-11-20 → HSCEI
- s3_envelope:NIKKEI225@2026-11-20 → NIKKEI225
- s3_envelope:DAX@2026-11-20 → DAX
- s3_envelope:CAC40@2026-11-20 → CAC40
- s3_envelope:VIX@2026-11-20 → VIX
- s3_envelope:NVDA@2026-11-20 → NVDA
- s3_envelope:AAPL@2026-11-20 → AAPL
- s3_envelope:MSFT@2026-11-20 → MSFT
- s3_envelope:TLT@2026-11-20 → TLT
- s3_envelope:IEF@2026-11-20 → IEF
- s3_envelope:SHY@2026-11-20 → SHY
- s3_envelope:HYG@2026-11-20 → HYG
- s3_envelope:LQD@2026-11-20 → LQD
- s3_envelope:DXY@2026-11-20 → DXY
- s3_envelope:EURUSD@2026-11-20 → EURUSD
- s3_envelope:GBPUSD@2026-11-21 → GBPUSD
- s3_envelope:USDJPY@2026-11-20 → USDJPY
- s3_envelope:USDCNY@2026-11-21 → USDCNY
- s3_envelope:GOLD_F@2026-11-20 → GOLD_F
- s3_envelope:SILVER_F@2026-11-20 → SILVER_F
- s3_envelope:WTI_F@2026-11-20 → WTI_F
- s3_envelope:BRENT_F@2026-11-20 → BRENT_F
- s3_envelope:GLD@2026-11-20 → GLD
- s3_envelope:USO@2026-11-20 → USO
- s3_envelope:EEM@2026-11-20 → EEM
- s3_envelope:EZU@2026-11-20 → EZU
- s3_envelope:FEZ@2026-11-20 → FEZ
- s3_envelope:EWU@2026-11-20 → EWU
- s3_envelope:EWG@2026-11-20 → EWG
- s3_envelope:EWJ@2026-11-20 → EWJ
- s3_envelope:INDA@2026-11-20 → INDA
- s3_envelope:FXI@2026-11-20 → FXI
- s3_envelope:BTC@2026-11-20 → BTC
- s3_envelope:HY_OAS@2026-11-19 → HY_OAS
- s3_envelope:BB_OAS@2026-11-19 → BB_OAS
- s3_envelope:B_OAS@2026-11-19 → B_OAS
- s3_envelope:CCC_OAS@2026-11-19 → CCC_OAS
- s3_envelope:IG_OAS@2026-11-19 → IG_OAS
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 问题未词面命中任何指标(零模型不做语义翻译);事实面降级为经济体概览,接地问答步骤仍如实作答/拒答
