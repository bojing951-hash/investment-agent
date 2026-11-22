# 一键研究报告(零模型编排 v2.0)
- 问题: 2026年11月,日本和欧元区的通胀与政策环境:两地央行当前官方政策目标利率各处于什么水平?最近六个月有无已决议但尚未生效的调整?两地通胀同比最新读数相比去年同月如何?请给出具体数据和各数据的公布时间。
- 运行: 20261122T141156Z @ ca916cdca7b749282e498d8c8f0eac8bf43b7372
- 快照: research_snapshot_20261122_v2 (target 20261122)
- 数据门(gate_a): 42/42 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 欧元区(EA)、日本(JP) | 维度 通胀、货币政策 | 计划指标 6 项 | 对照点锚 6个月前@2026-05-22、最新一期@2026-11-22 | 事后偏移+(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖12 观测),缺口 6 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: EA_HICP_YOY(缺什么: EA_HICP_YOY——任务窗窗口成员/覆盖不满足;问题指定了时间范围但无法解析: 问题声明多个时间范围约束(过去6个月·去年·2026年11月),单窗口接口无法表达多范围任务;请拆分为多个问题,分别声明单一时间范围(指定了范围但无法解析=阻断,不回落 max_available;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO——任务窗窗口成员/覆盖不满足;问题指定了时间范围但无法解析: 问题声明多个时间范围约束(过去6个月·去年·2026年11月),单窗口接口无法表达多范围任务;请拆分为多个问题,分别声明单一时间范围(指定了范围但无法解析=阻断,不回落 max_available;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR——任务窗窗口成员/覆盖不满足;问题指定了时间范围但无法解析: 问题声明多个时间范围约束(过去6个月·去年·2026年11月),单窗口接口无法表达多范围任务;请拆分为多个问题,分别声明单一时间范围(指定了范围但无法解析=阻断,不回落 max_available;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_YOY(缺什么: JP_CPI_YOY——任务窗窗口成员/覆盖不满足;问题指定了时间范围但无法解析: 问题声明多个时间范围约束(过去6个月·去年·2026年11月),单窗口接口无法表达多范围任务;请拆分为多个问题,分别声明单一时间范围(指定了范围但无法解析=阻断,不回落 max_available;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_TOKYO_YOY(缺什么: JP_CPI_TOKYO_YOY——任务窗窗口成员/覆盖不满足;问题指定了时间范围但无法解析: 问题声明多个时间范围约束(过去6个月·去年·2026年11月),单窗口接口无法表达多范围任务;请拆分为多个问题,分别声明单一时间范围(指定了范围但无法解析=阻断,不回落 max_available;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_POLICY_RATE(缺什么: JP_POLICY_RATE——任务窗窗口成员/覆盖不满足;问题指定了时间范围但无法解析: 问题声明多个时间范围约束(过去6个月·去年·2026年11月),单窗口接口无法表达多范围任务;请拆分为多个问题,分别声明单一时间范围(指定了范围但无法解析=阻断,不回落 max_available;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 6910.39 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-20]
- NDX = 25028.98 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-20]
- RUT = 2581.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-20]
- DXY = 103.81 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-20]
- EURUSD = 1.1 usd_per_eur @2026-11-20 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-20]
- GOLD_F = 3515.4 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-20]
- SILVER_F = 41.03 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-20]
- BRENT_F = 92.57 usd_per_barrel @2026-11-20 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-20]
- VIX = 35.89 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-20]
- DAX = 24802.78 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-20]
- CAC40 = 7927.75 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-20]
- USDJPY = 159.71 jpy_per_usd @2026-11-20 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-20]
- USDCNY = 6.66 cny_per_usd @2026-11-21 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-21]
- HY_OAS = 3.52 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-19]
- BB_OAS = 2.1 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-19]
- B_OAS = 3.8 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-19]
- CCC_OAS = 13.61 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-19]
- IG_OAS = 0.94 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-19]
- UST_2Y = 4.76 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-11-19]
- UST_10Y = 5.04 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-19]
- UST_30Y = 5.4 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_30Y@2026-11-19]
- TIPS_5Y = 2.64 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:TIPS_5Y@2026-11-19]
- TIPS_10Y = 2.88 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:TIPS_10Y@2026-11-19]
- BEI_5Y = 2.18 percent @2026-11-20 [质量:PASS] [来源:snapshot_fact:BEI_5Y@2026-11-20]
- BEI_10Y = 2.15 percent @2026-11-20 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-20]
- CURVE_2S10S = 0.29 percentage_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-11-20]
- UST_5Y = 4.86 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-19]
- SHCOMP = 3533.7929 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-20]
- HSI = 22410.8 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-20]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- JP_CPI_YOY = 2.44 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-10-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1-INFL-DIVERGE**: 两地通胀同比最新读数相比去年同月方向相反。日本全国CPI同比最新读数百分之二点四四(观测 2026-10,发布 2026-11-20,推定规则=总务省全国CPI次月中旬发布·月末+20天),去年同月(2025-10)为百分之二点九九,回落约零点五五个百分点;欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16,推定规则=Eurostat 终值次月中旬发布·月末+16天),去年同月(2025-10)为百分之二点一,抬升一点九个百分点——同期对照呈「日本回落、欧元区接近翻倍抬升」。东京都CPI同比(速报先行口径)最新可见读数为 2026-09 的百分之二点六九(发布 2026-10-25,推定),其序列自 2026-01 起,去年同月基期观测不可得、同比对照不可判。两条最新读数 L1 quality_status 均 WARN。
  - 竞争性解释1: 【假设】若欧元区抬升主要源于能源与进口价格的持续传导、而日本读数回落主要反映 2025 年秋季高基数消退,则 headline 同比的两地剪刀差应在未来数月收敛——引擎无分项构成与基数贡献序列,此归因不可在引擎面验证。
  - 竞争性解释2: 【假设】若两地差异主要由需求与政策组合驱动(欧元区内需偏热 vs 日本紧缩压制),则后续核心口径与读数路径应持续分化——同样缺分项与需求面证据,两种解释不可区分,如实并列。
  - 证据: JP_CPI_YOY@2026-10-01, EA_HICP_YOY@2026-10-01
- **C2-POLICY-SYNC**: 两地政策利率同向收紧,最近六个月(2026-05-22..2026-11-22)可核行动均已生效、无未生效决议。欧元区方面: 欧央行主要再融资利率(政策目标口径)最新生效水平百分之二点六五,观测=生效日 2026-09-16,决议日 2026-09-10,决议日当日公布。欧央行存款便利利率(操作下限口径)最新生效水平 2.50%,同决议(2026-09-10)、同日生效(2026-09-16)。窗内两次上调(2026-06-11 决议、2026-06-17 生效;2026-09-10 决议、2026-09-16 生效),幅度与路径见走位对照,均已生效。日本方面: 政策目标利率(宣布值口径,发布日历最新实录·2026-11-21 更新)约一点二五,2026-09-18 决议、2026-09-24 生效,2026-10-30 会议确认维持不变(无新调整、无生效变动);市场口径无担保隔夜拆借利率(月均)最新一期报 1.227%,六个月前锚前值为零点七二七,月均口径非宣布值。截至研究截止 2026-11-22,引擎记录面(注册表序列+发布日历实录)无任何已决议而尚未生效的调整。
  - 竞争性解释1: 【假设】若两地收紧主要由通胀读数驱动,则后续决议节奏应与读数联动——欧元区 4.0% 高位下紧缩延续概率高,日本读数回升下正常化延续。
  - 竞争性解释2: 【假设】若收紧主要反映政策正常化程序与汇率/金融稳定考量(日本尤甚),则决议节奏可与当期读数脱钩——月频证据下两种驱动不可区分,且引擎无央行表态文本序列。
  - 证据: ECB_MRO@2026-09-16, ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01
- **C3-ECB-VISIBILITY**: ECB 数据面断档使 2026-09-16 之后的决议面在引擎不可见。ECB_MRO/ECB_DFR 序列最后观测均为 2026-09-16,当日快照 Gate A 两序列列于 degraded 名单(源端缺席),L1 事实行 quality_status=DEGRADED;发布日历(最新版,2026-11-21 更新)对 ECB 无实录条目,「决议日=生效日前上一个周四」的推定只对已入序列的变更可用。因此「09-16 之后是否有新决议(含已决议未生效)」在引擎面不可判,属【尚未验证】;本报告关于 ECB 无未生效决议的结论仅覆盖引擎可见面。
  - 竞争性解释1: 若断档纯为源端技术缺席(生产观察登记 ECB 504)而实际无新决议,则 2.65%/2.50% 即最新水平,与 2026-09-10 决议后无新事件相容。
  - 竞争性解释2: 若断档期间实际发生了新决议,则当前读数低估最新水平——两种解释在引擎面不可区分,需官网核对方可裁(引擎外补充,须单独标注,待用户授权)。
  - 证据: ECB_DFR@2026-09-16, ECB_MRO@2026-09-16
- **机制链 M1-INFL-POLICY-ASSET**: 
  - E1 观察: 通胀路径——EA_HICP_YOY 自 2026-02 的 1.9 升至 2026-05 的 3.2(2026-06 一度回落至 2.8)、2026-10 达 4.0;JP_CPI_YOY 自 2025-11 高点 2.9 回落至 2026-02 的 1.27,此后总体回升至 2026-10 的 2.44(2026-04 一度微降至 1.38)。 [证据: EA_HICP_YOY@2026-10-01, JP_CPI_YOY@2026-10-01]
  - E1 观察: 政策面跟进——ECB 2026-06-11 决议(2026-06-17 生效)与 2026-09-10 决议(2026-09-16 生效)各 +25bp;BOJ 2026-09-18 决议(2026-09-24 生效)目标约 1.25%(发布日历实录),月均口径 0.727→1.227 的台阶与决议-生效记录相容。 [证据: ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01]
  - E2 传导【假设】: 若政策利差主导汇率,两地同向收紧但水平差(MRO 2.65% vs BOJ 目标约 1.25%)应体现于 EURUSD/USDJPY 方向——本引擎利率→汇率为近零渠道(无本地数据支持方向依据);当前仅水平观测(EURUSD 1.10、USDJPY 159.71,均观测 2026-11-20),方向对质不可判。 [缺失环: 引擎无政策差-汇率联动通道证据(近零渠道),该环为【假设】;区分指标=EURUSD/USDJPY,方向留白不裁。]
  - E2 资产面观察与对照: 近一月(2026-10-22→2026-11-20)NIKKEI225 下跌 10.29%、DAX 下跌 2.24%、SPX 下跌 9.83%,VIX 由 19.03 升至 35.89(+88.6%)——三地股指同跌、波动率大幅抬升;该组合与「紧缩+通胀粘性压制估值」与「全局风险/流动性冲击」两种叙事均相容,单一归因于两地政策不可证。 [缺失环: 归因环节为【假设】(单月窗、多因子叠加);区分指标=VIX,须待后续窗复检方向是否与政策日历联动。]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-STICKY-TIGHTEN**()
  - 情景: 【假设·非预测】通胀粘性延续: 至 2027-02,欧元区 HICP 同比维持 3.5% 以上、ECB 再有至少一次 +25bp 上调(决议后按惯例生效);日本全国 CPI 同比维持 2.0% 以上、BOJ 政策目标再上调一级(或月均中枢续升)。
  - 资产方向判断: 在此假设下,两地无风险利率与实际利率中枢承压上行,利率敏感资产(高估值股指)相对承压、波动率维持高位;此为方向性推演,非幅度预测(置信: 有相关证据) 
  - 敏感变量: EA_HICP_YOY, JP_CPI_YOY
  - 证伪指标: EA_HICP_YOY 阈值 若 2026-12 与 2027-01 两月欧元区 HICP 同比均回落至 3.0% 以下,粘性假设被证伪
  - 触发条件: 2026-12 或 2027-01 发布的 EA_HICP_YOY 同比 ≥4.0% 且 JP_CPI_YOY 同比 ≥2.0%,同时 VIX 高于 30(时限 2027-02-15)
- **S2-INFL-FADE**()
  - 情景: 【假设·非预测】当前欧元区通胀抬升以一次性因素(能源基数、进口传导)为主: 至 2027-02,EA_HICP_YOY 同比回落至 3.0% 以下、ECB 按兵不动;日本全国 CPI 同比回落至 2.0% 以下、BOJ 维持目标约 1.25% 不变。
  - 资产方向判断: 在此假设下,通胀预期与实际利率回落,风险资产修复、波动率回落;该方向与近一月观察(三地股指同跌、VIX 抬升)相反,属并列反例情景(置信: 纯逻辑推理) 
  - 敏感变量: EA_HICP_YOY, JP_CPI_YOY
  - 证伪指标: EA_HICP_YOY 阈值 若 2026-12 与 2027-01 两月 EA_HICP_YOY 同比均不低于 4.0%,一次性因素假设被证伪
  - 触发条件: EA_HICP_YOY 同比连续两个月回落且最新值 ≤3.4%,同时 VIX 回落至 25 以下(时限 2027-02-15)

## 语义审查(席位已裁)

- 席位裁决: REVISE(档: audit/semantic_review/20261122/VERDICT-20261122T141156Z-01.json)

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

## 日度相关(引擎确定性面·读者版)

- EA_HICP_YOY×ECB_MRO 日收益×日变化 pearson = 0.264(n=45 对,共同窗 1999-01..2026-09;描述性统计≠因果)


## Agent 判断落位

- attached=True(schema 1.1;violations=0)

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
- [OK |语义✔] S4_history_UST_30Y 
- [OK |语义✔] S4_history_TIPS_5Y 
- [OK |语义✔] S4_history_BEI_5Y 
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
- [OK |语义✔] S5_compare 命中 36 个指标,compare 仅取注册表序前 2(EA_HICP_YOY,ECB_MRO);其余 ECB_DFR,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,UST_30Y,TIPS_5Y,BEI_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(60 行)

- snapshot_fact:SPX@2026-11-20 → SPX
- snapshot_fact:NDX@2026-11-20 → NDX
- snapshot_fact:RUT@2026-11-20 → RUT
- snapshot_fact:DXY@2026-11-20 → DXY
- snapshot_fact:EURUSD@2026-11-20 → EURUSD
- snapshot_fact:GOLD_F@2026-11-20 → GOLD_F
- snapshot_fact:SILVER_F@2026-11-20 → SILVER_F
- snapshot_fact:BRENT_F@2026-11-20 → BRENT_F
- snapshot_fact:VIX@2026-11-20 → VIX
- snapshot_fact:DAX@2026-11-20 → DAX
- snapshot_fact:CAC40@2026-11-20 → CAC40
- snapshot_fact:USDJPY@2026-11-20 → USDJPY
- snapshot_fact:USDCNY@2026-11-21 → USDCNY
- snapshot_fact:HY_OAS@2026-11-19 → HY_OAS
- snapshot_fact:BB_OAS@2026-11-19 → BB_OAS
- snapshot_fact:B_OAS@2026-11-19 → B_OAS
- snapshot_fact:CCC_OAS@2026-11-19 → CCC_OAS
- snapshot_fact:IG_OAS@2026-11-19 → IG_OAS
- snapshot_fact:UST_2Y@2026-11-19 → UST_2Y
- snapshot_fact:UST_10Y@2026-11-19 → UST_10Y
- snapshot_fact:UST_30Y@2026-11-19 → UST_30Y
- snapshot_fact:TIPS_5Y@2026-11-19 → TIPS_5Y
- snapshot_fact:TIPS_10Y@2026-11-19 → TIPS_10Y
- snapshot_fact:BEI_5Y@2026-11-20 → BEI_5Y
- snapshot_fact:BEI_10Y@2026-11-20 → BEI_10Y
- snapshot_fact:CURVE_2S10S@2026-11-20 → CURVE_2S10S
- snapshot_fact:UST_5Y@2026-11-19 → UST_5Y
- snapshot_fact:SHCOMP@2026-11-20 → SHCOMP
- snapshot_fact:HSI@2026-11-20 → HSI
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-10-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-20 → SZCI
- s3_envelope:CHINEXT@2026-11-20 → CHINEXT
- s3_envelope:HSCEI@2026-11-20 → HSCEI
- s3_envelope:NVDA@2026-11-20 → NVDA
- s3_envelope:AAPL@2026-11-20 → AAPL
- s3_envelope:MSFT@2026-11-20 → MSFT
- s3_envelope:TLT@2026-11-20 → TLT
- s3_envelope:IEF@2026-11-20 → IEF
- s3_envelope:SHY@2026-11-20 → SHY
- s3_envelope:HYG@2026-11-20 → HYG
- s3_envelope:LQD@2026-11-20 → LQD
- s3_envelope:GBPUSD@2026-11-21 → GBPUSD
- s3_envelope:WTI_F@2026-11-20 → WTI_F
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
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): EA_HICP_YOY、ECB_MRO、ECB_DFR、JP_CPI_YOY、JP_CPI_TOKYO_YOY、JP_POLICY_RATE
