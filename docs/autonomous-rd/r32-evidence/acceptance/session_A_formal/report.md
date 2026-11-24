# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261123T235103Z @ 36499bb78a18dea1ff2b027074088b0ba404c3b8
- 快照: research_snapshot_20261123 (target 20261123)
- 数据门(gate_a): 61/61 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-23、3个月前@2026-08-23、最新一期@2026-11-23 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 研究截止日(证据口径 r32): 2026-11-23 | 源快照 research_snapshot_20261123(版本日 2026-11-23) | 事实: 保留 105 / 重建 0 / 剔除 0+版本 0 | 序列剔观测 0 | 版本不可得剔除 0 个观测 | 快照版本日口径(截止日=快照版本日)
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 8 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=16<130(日历期望261×半额;总量16不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-23..2026-11-23)——任务窗窗口成员/覆盖不满足;任务窗2025-11-23..2026-11-23未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 7203.85 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-23]
- NDX = 26672.85 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-23]
- RUT = 2581.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-20]
- DXY = 104.08 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-23]
- EURUSD = 1.09 usd_per_eur @2026-11-23 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-23]
- GOLD_F = 3685.2 usd_per_oz @2026-11-23 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-23]
- SILVER_F = 43.88 usd_per_oz @2026-11-23 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-23]
- BRENT_F = 88.19 usd_per_barrel @2026-11-23 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-23]
- VIX = 27.01 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-23]
- DAX = 25209.45 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-23]
- CAC40 = 8022.62 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-23]
- USDJPY = 159.35 jpy_per_usd @2026-11-23 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-23]
- USDCNY = 6.65 cny_per_usd @2026-11-23 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-23]
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
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- UST_5Y = 4.86 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-19]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- SHCOMP = 3538.948 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-23]
- HSI = 22383.74 index_point @2026-11-23 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-23]
- CN_LPR_1Y = 3.0 percent @2026-11-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-11-20]
- CN_CPI_YOY = 0.7 percent @2026-10-31 [质量:WARN] [来源:snapshot_fact:CN_CPI_YOY@2026-10-31]
- CN_PPI_YOY = 5.7 percent @2026-10-31 [质量:WARN] [来源:snapshot_fact:CN_PPI_YOY@2026-10-31]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- DFF = 3.88 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:DFF@2026-11-19]
- DFEDTARU = 4.0 percent @2026-11-23 [质量:PASS] [来源:snapshot_fact:DFEDTARU@2026-11-23]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- JP_CPI_YOY = 2.44 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-10-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1**: 主线综合: 过去12个月(至2026-11-23)四地证据面呈现『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动(其中资产收缩一腿属于近月窗口的事实，全年窗口内股指并未下行，窗口对照披露见机制链资产环)——CPI 与 CORE_PCE 同比较一年前走高(2026-05 见顶后回落、未再越过高点)、EA_HICP_YOY 升至本轮最高、CN_PPI_YOY 自负转正并续创本轮新高、CN_PMI_MFG 于 2025-12 及 2026-03、2026-04、2026-06、2026-09 共五个月站上荣枯线、其余月份不高于荣枯线(2026-05 持平于五十，余在四十九点零至四十九点八之间)、DFF 回到 2025-12 降息前的台阶附近(现 3.88)、ECB_DFR 两度上调、JP_POLICY_RATE 持续上行、UST_10Y 与 TIPS_10Y 上行而 BEI_10Y 回落、SPX 与 NIKKEI225 与 GOLD_F 近月收缩而 DXY 与 VIX 走高。该共动格局成立;但对『谁驱动谁』至少有三种数据同样容纳的解释(见竞争解释),当前证据不足以在它们之间裁决(其中解释C 的套息平仓一腿在同窗未获区分指标面支持，见传导面竞争链；其技术面一腿不可检验)——区分依赖 BEI_10Y 与 TIPS_10Y 的分解走向、HY_OAS 与 USDJPY 的后续观测(传导面对质三件见 reader_map.transmission)。证据面最新水平(引擎回贴,观测日至2026-11-23): UST_10Y 水平为 5.04、TIPS_10Y 水平为 2.88、BEI_10Y 水平为 2.15、VIX 水平为 27.01、HY_OAS 水平为 3.52、USDJPY 水平为 159.35、DFF 水平为 3.88、JP_POLICY_RATE 水平为 1.227、CN_PPI_YOY 水平为 5.7、CN_CPI_YOY 水平为 0.7、CN_PMI_MFG 水平为 49.3。其中 VIX 与 USDJPY 为 2026-11-23 盘中快照(非收盘价)。数据面披露: 本轮 Gate A 判 DEGRADED——核心缺口零项、非核心缺口七项、非核心降级八项，缺口指标中有五项在序列库内仍有存量观测并被本档按存量观测引用(属采集步骤降级口径，逐项见质量注记)。
  - 竞争性解释1: 解释A(主链): 通胀再加速(2026-02至2026-05美欧消费价格与中国生产价格同窗共振)迫使央行再收紧,名义利率上行由实际利率主导(12个月实际+102bp),高实际利率压制风险资产估值并推升 DXY、压低 GOLD_F——若成立,BEI_10Y 应大体稳定而 TIPS_10Y 续升
  - 竞争性解释2: 解释B(增长担忧): 风险资产收缩主要由增长预期下修驱动(美国工业同比一度折半、GDP 同比放缓),利率变化是结果而非原因——若成立,BEI_10Y 应主导性下行(衰退定价)而 TIPS_10Y 转平或回落;近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释的盈亏平衡一腿相容、与实际利率一腿相左, 整体仅部分相容
  - 竞争性解释3: 解释C(跨边境溢出/技术面): JP_POLICY_RATE 全年步进式正常化经由套息与久期渠道放大全球资产波动,或仓位/流动性技术因素主导近月收缩——若成立,USDJPY 与风险资产的波动应在时间上更紧地耦合,且 HY_OAS 应保持平稳(非信用事件)；同窗核验(见传导面竞争链): 该解释的套息平仓一腿未获区分指标面支持，技术面一腿不可检验
  - 证据: CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01, CN_PPI_YOY@2026-10-31, DFF@2026-11-19, ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01, UST_10Y@2026-11-19, TIPS_10Y@2026-11-19, BEI_10Y@2026-11-20, SPX@2026-11-23, NIKKEI225@2026-11-20, GOLD_F@2026-11-23, DXY@2026-11-23, VIX@2026-11-23, HY_OAS@2026-11-19, USDJPY@2026-11-23
- **C2**: 历史相似段的证据冲突: 三个最相似候选(2025-03、2022-06、2023-10)的事后路径分歧明显——2022-06段股指三个月窗普遍收缩(DAX、SHCOMP、SPX、NIKKEI225 均为负)而十二个月窗除 SHCOMP 外转正;2025-03、2023-10段风险资产与 GOLD_F 多数窗走强(2023-10段上证指数三个月窗为负，属例外)而 DXY 走弱;TOP-N事后符号一致率: GOLD_F 与 SPX 六个月与十二个月窗符号一致(一致率面仅含 DXY、GOLD_F、SPX、UST_10Y 四类)，其余各窗零点六至零点八。据此『当前状态可外推某一段事后路径』的主张不成立: 历史段只作结构对照与情景校准,不作预测(相似≠因果≠预测,分歧出现=结论降级为描述性)。所附四项引用为四项资产的当前水平锚点(供对照，不承载历史段数字)；历史段事后数字取自相似检索面事后块，按自然月末口径，事后结果≠预测。
  - 竞争性解释1: 解释A: 三段事后差异主要由各自独有的政策与冲击环境造成(2022-06 处加息中段、2023-10 处高利率平台期、2025-03 处波动冲击后修复)——事件叙述均为【假设】,引擎面不含事件因果数据
  - 竞争性解释2: 解释B: 差异由相似度量本身的低维覆盖造成(状态向量 growth 覆盖0.17、inflation 0.33、credit 0.5,信用维在多数候选月缺席),距离最近的时期未必在未覆盖维上可比——若如此,任何单段外推都缺失维度证据
  - 证据: SPX@2026-11-23, UST_10Y@2026-11-19, GOLD_F@2026-11-23, DXY@2026-11-23
- **C3**: 中国政策与美欧日方向的背离未被解释定案: CN_PPI_YOY 自深负值区间升至本轮高点(四大经济体最大价格摆动)而 CN_LPR_1Y 与 7天逆回购利率窗内持平(7天逆回购末观测 2026-10-30，其后缺观测)、政策利率锚于2026-11-02切换为隔夜利率工具后新锚持平于其首个观测水平,即生产价格大幅上行而政策利率未上调。引擎面无中国利率预期序列;信贷/内需侧仅有 CN_NEW_LOANS(月频，最新观测月 2026-10)等少量事实，不足以在三种解释间裁决,三种解释不可区分,标注【尚未验证】。(最新读数: CN_PPI_YOY 为 5.7、CN_CPI_YOY 为 0.7、CN_PMI_MFG 为 49.3;观测月均为 2026-10)。
  - 竞争性解释1: 解释A: 价格上行主要为输入型/供给驱动(PPI 与 CPI 剪刀差大),内需(CN_CPI_YOY 仅0.7)不足以支持收紧——若如此,背离是合理的政策反应
  - 竞争性解释2: 解释B: 内需不足制约政策空间(增长侧 CN_PMI_MFG 最新49.3处荣枯线下),即便价格上行也不敢收紧——若如此,背离反映的是增长约束而非价格判断
  - 竞争性解释3: 解释C: 汇率/资本流动目标约束政策选择——引擎面无中国资本流动序列,该解释当前不可裁决,标注【尚未验证】；汇率腿的可见事实: USDCNY 12 个月 -6.19%(7.1075→6.6676，共同口径 2025-11-19→2026-11-19)，人民币窗内升值，不支持『贬值/外流压力制约加息』的读法
  - 证据: CN_PPI_YOY@2026-10-31, CN_CPI_YOY@2026-10-31, CN_LPR_1Y@2026-11-20, USDCNY@2026-11-23
- **机制链 M1**: 
  - E1 冲击环【事实/E1】: 2026-02→2026-05 美欧通胀与中国生产价格同窗回升(美国CPI同比2.434→4.1666、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY -0.9→3.9，中国CPI同比同窗持平于一点零至一点三、消费价格未共振),此后至最新观测月: 美国 CORE_PCE 同比自 2026-05 高点 3.16 回落后部分回升(2026-07 3.00 → 2026-09 3.12，未再越过高点)、EA_HICP_YOY 2026-06回落至 2.8 后升至 4.0@2026-10、CN_PPI_YOY 2026-07回落至 3.5 后升至 5.7@2026-10。 [证据: CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01, CN_PPI_YOY@2026-10-31]
  - E3 政策环【时序为事实,动机为假设/E3】: 时序上政策再收紧的变动月(2026-06起: ECB 决议2026-06-11生效2026-06-17、决议2026-09-10生效2026-09-16(决议日系引擎回推【推断】);美联储决议2026-09-16生效2026-09-17回补此前降息;日本央行决议2026-09-18生效2026-09-24)在通胀转折月(至2026-05)之后;『央行因通胀再加速而收紧』的动机归因不可由本引擎数据验证,整环为【假设】,证伪指标=CPI(若 CPI 同比回落至2.5以下而央行仍续紧,动机环被证伪)。须披露: 按引擎发布规则，2026-09 三次收紧决议时点前已可见的美国 CPI 同比已自 2026-05 高点 4.17 回落(欧央行 2026-09-10 决议前最近可见 2026-07 观测 3.30；美联储 2026-09-16 与 日本央行 2026-09-18(生效 2026-09-24) 决议前最近可见 2026-08 观测 3.35)，欧央行 2026-06-11 决议前最近可见 2026-04 观测 3.78 仍处上行段——『因通胀续升而收紧』对美联储与欧央行第二次决议前的可见数据不完全吻合(美联储另见核心 PCE 同比: 2026-07 观测 3.00，低于 2026-05 高点 3.16；欧央行 2026-09-10 决议前最近可见 HICP 为 2026-07 观测 2.9，自 2026-06 的 2.8 回升、低于 2026-05 高点 3.2，2026-08 观测 3.2 按引擎规则推定发布于 2026-09-16、决议时点尚未可见)，对日本央行则未见该矛盾(2026-09-18 决议前最近可见日本CPI为 2026-07 观测 1.97，处回升段，与收紧动机相容但同样不可验证)——三家的动机归因均不可由本引擎数据验证，对美联储与欧央行的动机环证据减弱。决议后发布的 2026-09 观测回升至 3.72(仍低于高点 4.17；2026-10 同比缺基期不可得)。 [证伪指标: CPI]
  - E1 利率环【事实/E1】: 12个月窗(2025-11-19→2026-11-19共同交易日)十年期美债名义+91bp=实际(TIPS_10Y)+102bp+盈亏平衡(BEI_10Y)-11bp,恒等残差0;水平 UST_10Y 5.04、TIPS_10Y 2.88、BEI_10Y 2.16@2026-11-19(共同交易日；最新 2.15@2026-11-20)——名义上行几乎全部由实际利率贡献,市场通胀预期(盈亏平衡)反而回落。 [证据: UST_10Y@2026-11-19, TIPS_10Y@2026-11-19, BEI_10Y@2026-11-20]
  - E2 资产环【E2,缺环为假设】: 近1个月(2026-10-23→2026-11-19/20/23)SPX -5.51%、NIKKEI225 -9.98%、GOLD_F -8.05%、DXY +2.23%、VIX 19.45→27.01(其中 SPX、GOLD_F、DXY、VIX 为 2026-11-23 盘中快照、非收盘价；同日收盘口径 2026-10-23→2026-11-20 标普500指数 -9.36%、VIX +84.52%),与『实际利率上行压制长久期/无现金流资产、推升美元』的机制相容(此共动限于近窗: 共同交易日 2026-10-20→2026-11-19 TIPS_10Y +11bp 对 SPX -6.96%、2026-08-19→2026-11-19 +53bp 对 -6.90%；而12个月窗 2025-11-19→2026-11-19 实际利率 +102bp 与 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93% 同向上行，12个月窗内未见『实际利率上行伴随股指下行』，共动方向随窗口而异);但资产与利率只有共动事实(相关≠因果),『利率变化导致估值变化』的传导环节本引擎无法直接验证,此环为【假设】;若为利率驱动，HY_OAS 应保持非信用事件级(当前 3.52pp(注册表单位为百分点)，低于 2025-04-07 序列高点 4.61，但处引擎三年历史约第 92 百分位)，证伪观察分两级: 预警级=HY_OAS 升破 2025-05-09 的 3.53(库内上一次不低于最新读数的水平)，失效级=升破 4.61 的序列高点(距最新读数 109 个基点，单用偏松；量化阈值，【假设】的可观察形态)。 [缺失环: 缺失环=利率变化→估值变化的因果传导(引擎只有共动事实,无因果识别);该环为【假设】,证伪指标=HY_OAS]
- **机制链 M2**: 
  - E1 【事实/E1】: JP_POLICY_RATE(无担保隔夜拆借月均)自 2025-11 月均 0.478(窗启时在值)步进升至 2026-10 月均 1.227(窗内净 +75 个基点；月度步进 +8/+17/+11/+14/+7/+18 个基点，分别落在 2025-12、2026-01、2026-06、2026-07、2026-09、2026-10，另有 2026-04 与 2026-08 各约零点一个基点的舍入变动；自 2025-12 月均 0.557 起为 +67 个基点，属另一口径),为四地中唯一在美欧通胀同窗回升(2026-02起)之前已开始上调、窗内未回撤的政策轨迹;发布日历实录载政策决议2026-09-18(生效2026-09-24);另载 2026-10-30 会议确认维持政策目标利率不变(确认维持不改变目标水平，只更新核验覆盖截止);USDJPY 水平159.35@2026-11-23(2026-11-23 盘中快照、非收盘价)。 [证据: JP_POLICY_RATE@2026-10-01, USDJPY@2026-11-23]
  - E3 【E3,整环假设】: 日本正常化推升日债收益率与全球期限溢价、经套息平仓放大风险资产波动——本引擎无 JGB 历史序列(单点观测),整环不可验证,为【假设】;证伪指标=USDJPY(若风险资产再次收缩而 USDJPY 未同步走低/日元未走强,套息平仓渠道的分量应被下调)。 [证伪指标: USDJPY]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN1**(基准情景)
  - 情景: 基准情景(假设非预测): 假设通胀再加速延续(美国CPI同比保持在3以上)且欧/美/日维持收紧倾向、中国维持政策利率不变(未跟进加息),则实际利率维持高位、政策分化延续。
  - 资产方向判断: 在此假设下,股指(SPX/NIKKEI225)倾向承压或高波动、GOLD_F 受高实际利率与强美元双重压力、DXY 偏强、VIX 中枢抬升;该方向与2022-06相似段三个月窗(SPX -5.28%、GOLD_F -7.49%、DXY +7.10%,月末口径)一致,但同段十二个月窗 SPX 转正(+17.57%)——历史相似证据内部亦分歧。所引 2026-11-23 资产值为盘中快照(非收盘价)。(置信: 有历史相似证据) 
  - 敏感变量: TIPS_10Y, CPI
  - 证伪指标: CPI 阈值 美国CPI同比回落至2.5以下(2026-10 同比待 2025-10 基期补齐后再核；2026-11 起同比不受此缺基期影响)且 CORE_PCE 同比回落至2.8以下并持续两个月——通胀再加速前提失效,本情景资产方向判断随之失效
  - 触发条件: 美国2026-11或2026-12月CPI同比继续≥3.5,或欧央行/美联储再加息(生效日=DFEDTARU/ECB_DFR 序列变更日，决议日按引擎惯例自生效日回推【推断】；冻结发布日历暂无两家实录条目)(时限 2027-02-28)
- **SCN2**(反例情景)
  - 情景: 反例情景(假设非预测): 假设通胀再加速被证明为一次性(基数/供给消退),欧/美暂停并转向宽松预期,则盈亏平衡通胀回升而实际利率回落、政策分化收敛。
  - 资产方向判断: 在此假设下,股指倾向修复、GOLD_F 修复走强、DXY 转弱;该方向与2025-03相似段十二个月窗(GOLD_F +48.83%、DXY -4.08%、SPX +16.33%,月末口径)方向一致——注意该段相似度主要由波动维与利率维支撑(42.1%+40.7%)且事后窗与本轮早段重叠,样本非独立。所引 2026-11-23 资产值为盘中快照(非收盘价)。(置信: 有历史相似证据) 
  - 敏感变量: BEI_10Y, TIPS_10Y
  - 证伪指标: BEI_10Y 阈值 BEI_10Y 跌破1.8且继续下行(阈值依据: 库内最近一次低于 1.8 为 2020-11-30 的 1.77，较最新读数 2.15(2026-11-20)低 38 个基点(该读数较阈值 1.8 高 35 个基点)，作深跌确认线)——盈亏平衡通胀不回升反深跌,『一次性通胀+宽松预期修复』前提失效(深跌 BEI 指向衰退定价而非修复)
  - 触发条件: 欧央行或美联储下一次决议为降息或明确暂停指引(生效日=DFEDTARU/ECB_DFR 序列变更日，决议日按引擎惯例自生效日回推【推断】；冻结发布日历暂无两家实录条目),或美国CPI同比自 2026-11 观测月起连续两个月回落(2026-10 同比待 2025-10 基期补齐)(时限 2027-02-28)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.727212 | 0.0 | volatility 42.1%、rates 40.7% |
| 2 | 2022-06 | 0.791806 | 1.3699 | rates 51.9%、valuation 33.6% |
| 3 | 2023-10 | 1.054168 | 30.137 | volatility 60.1%、valuation 21.2% |
| 4 | 2021-02 | 1.284945 | 69.863 | rates 72.0%、volatility 18.4% |
| 5 | 2020-01 | 1.357685 | 71.2329 | rates 68.3%、volatility 14.6% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率
> **事后结果标注**: 候选月=事后筛得的相似结构(相似度用到候选月全窗口数据);候选月**之后**的经济与资产表现为事后结果(事后≠当时可知,事后≠预测)——引用须以「事后实际」措辞,不得表述为当时可知或对本次的预测(纪律17)。

## 日度相关(引擎确定性面·读者版)

- US_REAL_GDP×UNEMPLOYMENT 日收益×日变化 pearson = -0.8936(n=37 对,共同窗 2017-01..2026-07;描述性统计≠因果)


## Agent 判断落位

- attached=True(schema 1.1;violations=0)

## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_US 
- [OK |语义✔] S3_overview_CN 
- [OK |语义✔] S3_overview_EA 
- [OK |语义✔] S3_overview_JP 
- [OK |语义✔] S3_overview_GLOBAL 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_US_REAL_GDP 
- [OK |语义✔] S4_history_UNEMPLOYMENT 
- [OK |语义✔] S4_history_INDPRO 
- [OK |语义✔] S4_history_CPI 
- [OK |语义✔] S4_history_CORE_CPI 
- [OK |语义✔] S4_history_CORE_PCE 
- [OK |语义✔] S4_history_DFEDTARU 
- [OK |语义✔] S4_history_DFF 
- [OK |语义✔] S4_history_CN_PMI_MFG 
- [OK |语义✔] S4_history_CN_CPI_YOY 
- [OK |语义✔] S4_history_CN_PPI_YOY 
- [OK |语义✔] S4_history_CN_POLICY_OVERNIGHT 
- [OK |语义✔] S4_history_CN_OMO_7D 
- [OK |语义✔] S4_history_CN_LPR_1Y 
- [OK |语义✔] S4_history_EA_REAL_GDP_YOY 
- [OK |语义✔] S4_history_EA_HICP_YOY 
- [OK |语义✔] S4_history_ECB_MRO 
- [OK |语义✔] S4_history_ECB_DFR 
- [OK |语义✔] S4_history_JP_REAL_GDP_YOY 
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
- [OK |语义✔] S5_compare 命中 52 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,DFEDTARU,DFF,CN_PMI_MFG,CN_CPI_YOY,CN_PPI_YOY,CN_POLICY_OVERNIGHT,CN_OMO_7D,CN_LPR_1Y,EA_REAL_GDP_YOY,EA_HICP_YOY,ECB_MRO,ECB_DFR,JP_REAL_GDP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,UST_30Y,TIPS_5Y,BEI_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(72 行)

- snapshot_fact:SPX@2026-11-23 → SPX
- snapshot_fact:NDX@2026-11-23 → NDX
- snapshot_fact:RUT@2026-11-20 → RUT
- snapshot_fact:DXY@2026-11-23 → DXY
- snapshot_fact:EURUSD@2026-11-23 → EURUSD
- snapshot_fact:GOLD_F@2026-11-23 → GOLD_F
- snapshot_fact:SILVER_F@2026-11-23 → SILVER_F
- snapshot_fact:BRENT_F@2026-11-23 → BRENT_F
- snapshot_fact:VIX@2026-11-23 → VIX
- snapshot_fact:DAX@2026-11-23 → DAX
- snapshot_fact:CAC40@2026-11-23 → CAC40
- snapshot_fact:USDJPY@2026-11-23 → USDJPY
- snapshot_fact:USDCNY@2026-11-23 → USDCNY
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
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:UST_5Y@2026-11-19 → UST_5Y
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:SHCOMP@2026-11-23 → SHCOMP
- snapshot_fact:HSI@2026-11-23 → HSI
- snapshot_fact:CN_LPR_1Y@2026-11-20 → CN_LPR_1Y
- snapshot_fact:CN_CPI_YOY@2026-10-31 → CN_CPI_YOY
- snapshot_fact:CN_PPI_YOY@2026-10-31 → CN_PPI_YOY
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:DFF@2026-11-19 → DFF
- snapshot_fact:DFEDTARU@2026-11-23 → DFEDTARU
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-10-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-23 → SZCI
- s3_envelope:CHINEXT@2026-11-23 → CHINEXT
- s3_envelope:HSCEI@2026-11-23 → HSCEI
- s3_envelope:NVDA@2026-11-23 → NVDA
- s3_envelope:AAPL@2026-11-23 → AAPL
- s3_envelope:MSFT@2026-11-23 → MSFT
- s3_envelope:TLT@2026-11-23 → TLT
- s3_envelope:IEF@2026-11-23 → IEF
- s3_envelope:SHY@2026-11-23 → SHY
- s3_envelope:HYG@2026-11-23 → HYG
- s3_envelope:LQD@2026-11-23 → LQD
- s3_envelope:GBPUSD@2026-11-23 → GBPUSD
- s3_envelope:WTI_F@2026-11-23 → WTI_F
- s3_envelope:GLD@2026-11-23 → GLD
- s3_envelope:USO@2026-11-23 → USO
- s3_envelope:EEM@2026-11-23 → EEM
- s3_envelope:EZU@2026-11-23 → EZU
- s3_envelope:FEZ@2026-11-23 → FEZ
- s3_envelope:EWU@2026-11-23 → EWU
- s3_envelope:EWG@2026-11-23 → EWG
- s3_envelope:EWJ@2026-11-23 → EWJ
- s3_envelope:INDA@2026-11-23 → INDA
- s3_envelope:FXI@2026-11-23 → FXI
- s3_envelope:BTC@2026-11-22 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
