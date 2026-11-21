# 一键研究报告(零模型编排 v2.0)
- 问题: 近一个月VIX飙升而高收益债OAS利差几乎未动，信用市场是否对股市风险过于自满？
- 运行: 20261119T173250Z @ b316e88b2b4a98e95ab23aeac71a304485e78b0f
- 快照: research_snapshot_20261118 (target 20261118)
- 数据门(gate_a): 8/8 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 数据需求(运行前冻结): 必要 2 项(问题命中,规格=序列/最低覆盖60 观测),缺口 0 项;可选面缺席=降级披露不构成缺口

## 四层区分

### L1 事实层 available=True
- VIX = 25.46 index_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-17]
- HY_OAS = 3.34 percentage_point @2026-11-16 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-16]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CONTRA-1**: 近一个月 VIX 大幅上升: 计算窗口 2026-10-19 至 2026-11-17(界日 2026-10-18 最近邻,两端实测日与实测值见资产月窗表),月窗涨幅 +38.07%;同期高收益债利差 HY_OAS 月窗(2026-10-19 至 2026-11-16)仅走阔 +0.05pp——股市波动定价急剧上升而信用风险定价几乎未动,构成明显的跨市场定价张力。
  - 依据: 窗口与数字由引擎资产月窗面同一算术口径复算(≤2026-11-18 最新观测 vs 最近于界日的观测,两端实际观测日随行披露);美股股指 SPX 同窗(2026-10-19 至 2026-11-17)下跌 −4.55%,波动上升有股市下行背景,非单纯期权市场技术性抬升。
  - 竞争性解释1: 解释一(自满/滞后): 若信用市场对股市风险过于自满,则高收益债持有人将不被要求补偿波动冲击,利差定价将滞后于波动率,随后转入补涨式走阔。
  - 竞争性解释2: 解释二(基本面定价): 若本轮 VIX 上升主要由权益端事件性/仓位性因素驱动而违约概率预期未变,则 HY_OAS 的稳定将反映基本面定价而非自满。
  - 竞争性解释3: 解释三(结构性差异): 两指标口径不同构——VIX 是 30 天前瞻波动价格,HY_OAS 是含违约预期+期限溢价+流动性补偿的水平值;波动率冲击向违约预期的传导需要时间与信用事件催化,同月未动未必是定价错误。
  - 证据: VIX@2026-11-17, HY_OAS@2026-11-16, SPX@2026-11-17
- **机制链 MECH-1**: 波动冲击→信用利差传导链(区分自满与基本面定价)
  - E1 事实环: VIX 月窗 +38.07%(窗口 2026-10-19 至 2026-11-17,两端实测值见资产月窗表),同期 SPX 同窗下跌 −4.55%、HY_OAS 月窗(2026-10-19 至 2026-11-16)仅走阔 +0.05pp——三组数字同窗同口径,可复算。 [证据: VIX@2026-11-17, HY_OAS@2026-11-16, SPX@2026-11-17]
  - E2 推断环: 波动冲击向信用利差的传导当月未兑现。缺失环【假设】=违约概率预期未上升(无信用事件/盈利下修催化)——该环不可直接观测,以 HY_OAS 后续路径检验。 [缺失环: 假设: 违约概率预期在窗口内未变(缺失环),若该假设为真,HY_OAS 按兵不动是基本面定价而非自满。]
  - E3 叙事环: 若自满解释成立,信用利差应随后补涨走阔;若基本面解释成立,利差维持且 VIX 回落。区分指标=HY_OAS 本身: 自满=利差对已发生波动冲击的迟到反应,基本面=利差只因违约预期而动。 [证伪指标: HY_OAS]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**(基准(自满/滞后))
  - 情景: 假设信用市场自满: +38.07% 的波动冲击未被利差定价,未来 1-2 个月 HY_OAS 补涨走阔 ≥40bp,高收益债跑输国债与投资级。
  - 资产方向判断: 高收益债下跌(利差走阔),避险资产受益(置信: 有相关证据) 历史上波动率飙升而利差未动的组合多次以利差补涨收场(相关证据,非本窗内已兑现);当前窗口两端实测值支持起点事实。
  - 敏感变量: HY_OAS, VIX
  - 证伪指标: HY_OAS 阈值 至 2027-01-16 HY_OAS 仍 <3.50(较 2026-11-16 的 3.34 走阔不足 16bp)则本情景证伪
  - 触发条件: VIX 维持 >25 或再度上行且出现首笔高收益债违约/下修事件(时限 2026-12-31)
- **SCN-B**(反例(基本面定价正确))
  - 情景: 假设信用定价正确: 本轮波动为权益端事件性冲击,违约预期未变,HY_OAS 在 3.20-3.50 区间震荡,VIX 随事件消化回落至 20 附近。
  - 资产方向判断: 高收益债持有收益(carry)兑现,不出现补跌(置信: 纯逻辑推理) 以违约预期稳定为前提的逻辑推演(窗口内无信用事件证据,纯逻辑层);与解释三的结构性差异论相容。
  - 敏感变量: HY_OAS, VIX
  - 证伪指标: HY_OAS 阈值 至 2027-01-16 HY_OAS >3.75(走阔 >40bp)则本情景证伪
  - 触发条件: HY_OAS 两周内走阔 >20bp 或高收益债 ETF 持续资金流出(时限 2026-12-31)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.586681 | 0.0 | rates 66.3%、volatility 14.0% |
| 2 | 2022-06 | 0.777538 | 12.3288 | rates 53.2%、valuation 34.9% |
| 3 | 2023-10 | 0.849956 | 21.9178 | volatility 42.9%、valuation 32.6% |
| 4 | 2021-02 | 1.181508 | 68.4932 | rates 86.5%、inflation 6.6% |
| 5 | 2019-12 | 1.220424 | 73.9726 | rates 53.1%、volatility 29.9% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率

## 日度相关(引擎确定性面·读者版)

- VIX×HY_OAS 日收益×日变化 pearson = 0.5493(n=751 对,共同窗 2023-11-20..2026-11-16;描述性统计≠因果)


## Agent 判断落位

- attached=True(schema 1.1;violations=0)

## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_US 
- [OK |语义✔] S3_overview_CN 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_VIX 
- [OK |语义✔] S4_history_HY_OAS 
- [OK |语义✔] S5_compare 
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(46 行)

- snapshot_fact:VIX@2026-11-17 → VIX
- snapshot_fact:HY_OAS@2026-11-16 → HY_OAS
- s3_envelope:SPX@2026-11-17 → SPX
- s3_envelope:NDX@2026-11-17 → NDX
- s3_envelope:RUT@2026-11-17 → RUT
- s3_envelope:SHCOMP@2026-11-17 → SHCOMP
- s3_envelope:SZCI@2026-11-17 → SZCI
- s3_envelope:CHINEXT@2026-11-17 → CHINEXT
- s3_envelope:HSI@2026-11-17 → HSI
- s3_envelope:HSCEI@2026-11-17 → HSCEI
- s3_envelope:NIKKEI225@2026-11-17 → NIKKEI225
- s3_envelope:DAX@2026-11-16 → DAX
- s3_envelope:CAC40@2026-11-16 → CAC40
- s3_envelope:NVDA@2026-11-17 → NVDA
- s3_envelope:AAPL@2026-11-17 → AAPL
- s3_envelope:MSFT@2026-11-17 → MSFT
- s3_envelope:TLT@2026-11-17 → TLT
- s3_envelope:IEF@2026-11-17 → IEF
- s3_envelope:SHY@2026-11-17 → SHY
- s3_envelope:HYG@2026-11-17 → HYG
- s3_envelope:LQD@2026-11-17 → LQD
- s3_envelope:DXY@2026-11-17 → DXY
- s3_envelope:EURUSD@2026-11-17 → EURUSD
- s3_envelope:GBPUSD@2026-11-17 → GBPUSD
- s3_envelope:USDJPY@2026-11-17 → USDJPY
- s3_envelope:USDCNY@2026-11-17 → USDCNY
- s3_envelope:GOLD_F@2026-11-17 → GOLD_F
- s3_envelope:SILVER_F@2026-11-17 → SILVER_F
- s3_envelope:WTI_F@2026-11-17 → WTI_F
- s3_envelope:BRENT_F@2026-11-17 → BRENT_F
- s3_envelope:GLD@2026-11-17 → GLD
- s3_envelope:USO@2026-11-17 → USO
- s3_envelope:EEM@2026-11-17 → EEM
- s3_envelope:EZU@2026-11-17 → EZU
- s3_envelope:FEZ@2026-11-17 → FEZ
- s3_envelope:EWU@2026-11-17 → EWU
- s3_envelope:EWG@2026-11-17 → EWG
- s3_envelope:EWJ@2026-11-17 → EWJ
- s3_envelope:INDA@2026-11-17 → INDA
- s3_envelope:FXI@2026-11-17 → FXI
- s3_envelope:BTC@2026-11-16 → BTC
- s3_envelope:BB_OAS@2026-11-16 → BB_OAS
- s3_envelope:B_OAS@2026-11-16 → B_OAS
- s3_envelope:CCC_OAS@2026-11-16 → CCC_OAS
- s3_envelope:IG_OAS@2026-11-16 → IG_OAS
- s3_envelope:HY_IG_DIFF@2026-11-16 → HY_IG_DIFF

## 注记

- 问题未命中经济体,S3 用默认面 US+CN(清单默认,非问题语义判断;Agent 可按需补查其它经济体)
