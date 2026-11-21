# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261121T074411Z @ 48c03cb847ff985615c4f2254558d3a7f0be4b1a
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 59/59 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-21、3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 9 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<130(日历期望261×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_HICP_YOY(缺什么: EA_HICP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

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
- USDCNY = 6.68 cny_per_usd @2026-11-21 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-21]
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
- SHCOMP = 3533.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-20]
- HSI = 22410.8 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-20]
- CN_LPR_1Y = 3.0 percent @2026-11-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-11-20]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- JP_CPI_YOY = 2.44 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-10-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 1.9 percent @2025-12-01 [质量:DEGRADED] [来源:snapshot_fact:EA_HICP_YOY@2025-12-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1-us-inflation-policy**: 美国宏观组合从『通胀回落+政策宽松』切换为『通胀再加速+政策再紧缩』: 引擎面显示 CPI 与 CORE_PCE 同比在三锚点间逐级走高,而增长面仅温和放缓(US_REAL_GDP 同比小幅下行、INDPRO 同比回升、UNEMPLOYMENT 平稳)——这是政策面在降息后重新转向加息的宏观背景;该组合下政策路径对通胀数据的敏感度显著上升。
  - 依据: 依据证据索引 CPI、CORE_CPI、CORE_PCE、US_REAL_GDP、INDPRO、UNEMPLOYMENT 的锚点观测,以及引擎政策事件簇面(DFEDTARU 路径: 2025-12 降息后 2026-09 重启加息,簇内与 ECB 决议同窗合并计数)。
  - 竞争性解释1: 若通胀动能主要来自需求韧性(增长未失速、失业率平稳),则紧缩将持续更久、实际利率中枢上移,估值消化期更长
  - 竞争性解释2: 若通胀再加速主要来自能源与工业品的全球供给脉冲(引擎面 BRENT_F 与 CN_PPI_YOY 同期大幅走高与之相容),则通胀对政策收紧的响应更快、回落也可能更快
  - 竞争性解释3: 【假设】2025 年秋美国统计发布停摆造成的基期错位与发布延迟可能放大同比读数,通胀回升幅度或被高估——证伪指标: CORE_PCE(若后续修订/新基期下同比回落至停摆前趋势,该解释成立)
  - 证据: CPI@2026-10-01, CORE_CPI@2026-10-01, CORE_PCE@2026-09-01, US_REAL_GDP@2026-07-01, INDPRO@2026-10-01, UNEMPLOYMENT@2026-10-01
- **C2-nov-selloff-driver**: 最新月窗出现跨资产急跌: SPX 与 NIKKEI225 双位数百分比月跌幅、VIX 大幅冲高、GOLD_F 同月显著回落而 DXY 走高——『股票与黄金同跌+美元走强』的组合在月频分辨率下同时容纳两类机制: 政策再紧缩下实际利率上行对高估值的压制,与流动性收紧/去杠杆冲击;两者对后续通胀预期与信用利差的含义不同。
  - 依据: 依据证据索引 SPX、NIKKEI225、DAX、SHCOMP、VIX、GOLD_F、DXY、HY_OAS、UST_10Y 的最新观测、引擎月窗变化面(asset_moves),以及共同交易日利率三分解(数值随 reader_map.rates_decomposition 回贴;近30日名义下行=实际段上行+盈亏平衡下行)。
  - 竞争性解释1: 若实际利率快速上行是主因,则跌幅应集中于长久期与高估值资产、通胀预期基本锚定、信用利差仅温和走阔(引擎面 HY_OAS 十二个月变化温和与之相容)
  - 竞争性解释2: 若流动性冲击/去杠杆是主因,则黄金与股票同跌、美元走强、波动率飙升并存(最新月窗形态与之相容),且跨资产相关性趋于同向化
  - 竞争性解释3: 若增长担忧主导,则盈亏平衡通胀应明显下行且曲线加速趋平——三类机制可用 BEI_10Y 与 CURVE_2S10S 的后续轨迹区分
  - 证据: SPX@2026-11-20, NIKKEI225@2026-11-20, VIX@2026-11-20, GOLD_F@2026-11-20, DXY@2026-11-20, HY_OAS@2026-11-19, UST_10Y@2026-11-19
- **C3-policy-divergence**: 同一全球再通胀背景下四大央行反应分化: ECB 两度加息、日本持续正常化、美国降息后重启加息、中国政策利率全程不动——分化方向与各地增长-通胀组合的相对位置一致(中国 PMI 三期处于收缩区间、日本增长加速、美国通胀偏高、欧元区政策先行)。
  - 依据: 依据证据索引 ECB_DFR、ECB_MRO、JP_POLICY_RATE、CN_LPR_1Y、CN_PMI_MFG 观测与引擎政策事件簇面(2026-09 欧美决议同窗合并为同一全球政策事件)。
  - 竞争性解释1: 若分化主要由各地国内基本面驱动,后续政策路径将继续跟随各自通胀与增长数据(中国 PMI 修复至50上方前无加息压力)
  - 竞争性解释2: 【假设】若分化部分源于汇率与资本流动约束(如日元贬值压力影响日本加息节奏、中美利差影响中国宽松空间),则外部利差(美日、中美)是比国内通胀更好的同步指标——引擎面 USDJPY 与美日政策分化同向演变与之相容
  - 竞争性解释3: 若中国工业品再通胀向核心通胀传导加速,中国『按兵不动』存在边际调整可能——证伪指标: CN_CPI_YOY(若连续数月升至2以上,该解释被强化而非证伪;若停留在1以下,政策不动解释成立)
  - 证据: ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01, CN_LPR_1Y@2026-11-20, CN_PMI_MFG@2026-10-01
- **机制链 M1-us-reflation-tightening**: 
  - E1 环1(观察,通胀): 美国 CPI 同比从12个月前锚的 3.02 升至最近有效观测 3.72(2026-09,最新锚缺基期不可得),CORE_CPI 同比 2.57(2026-09 最近有效)、CORE_PCE 同比 2.85→3.12——通胀再加速为引擎点值面直接可验事实。 [证据: CPI@2026-10-01, CORE_CPI@2026-10-01, CORE_PCE@2026-09-01]
  - E1 环2(政策反应): 引擎政策事件簇面: 联储 2025-12-10 降25bp后于 2026-09-16 重启加息25bp(与 ECB 2026-09-10 决议同窗±7日,合并为同一全球政策事件 POLCLUSTER-03);ECB 2026-06-11、2026-09-10 各加25bp;日本 2026-04→07 窗政策利率续升。政策面转向可由 ECB_DFR/JP_POLICY_RATE 序列直接验证(DFEDTARU 逐次决议在引擎簇面)。 [证据: ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01]
  - E1 环3(利率结构): 共同交易日12个月窗(2025-11-19→2026-11-19)名义 UST_10Y +91bp 全部来自实际段(TIPS_10Y +102bp)而盈亏平衡 BEI_10Y −11bp;UST_2Y 12个月 +125bp(2025-11-21→2026-11-19 自配对原值)高于长端,CURVE_2S10S −26bp 走平——短端政策预期主导利率上行。 [证据: UST_10Y@2026-11-19, TIPS_10Y@2026-11-19, BEI_10Y@2026-11-20, UST_2Y@2026-11-19]
  - E1 环4(资产): 最新月窗 SPX −10.92%、NIKKEI225 −12.67%、DAX −3.28%、SHCOMP −4.83%,VIX 16.68→35.89(+115.17%),GOLD_F −15.29%、DXY +1.99%;HY_OAS 12个月 +33bp(自配对原值,3.19→3.52)温和走阔——跨资产调整为引擎月窗面原值。 [证据: SPX@2026-11-20, VIX@2026-11-20, GOLD_F@2026-11-20, NIKKEI225@2026-11-20, DXY@2026-11-20, HY_OAS@2026-11-19]
  - E2 环5(归因,估值敏感度): 实际利率快速上行在高估值环境(SPX_CAPE z=2.82,引擎 analog 状态面)放大股票久期重定价——此环为推断。 [缺失环: 引擎无『估值-实际利率弹性』序列,该环为【假设】;可验证替代观察: 若该环成立,BEI_10Y 应保持锚定而 SPX 与 TIPS_10Y 同步反向变动。]
- **机制链 M2-cn-reflation-commodity**: 
  - E2 环1(观察,中国再通胀): CN_PPI_YOY 同比 −2.1(2025-10)→3.5(2026-07)→5.7(2026-10),CN_CPI_YOY 0.2→0.7;同期美 CPI 同比 3.02→3.72(最近有效),BRENT_F 12个月 +47.97%(62.56→92.57,自配对原值)——中美价格共振与能源脉冲并存。 [缺失环: CN_PPI_YOY/CN_CPI_YOY 数值在研究计划点值格(引擎确定性面)但不在证据索引68行内,本环 E1 锚不可用;【假设】: 工业品价格回升沿企业定价与库存周期待导,引擎无中国工业库存序列。]
  - E1 环2(资产面): SHCOMP 最新月窗 −4.83%,跌幅浅于 SPX(−10.92%)与 NIKKEI225(−12.67%);HSI 最新观测 22410.8 在档——A股相对抗跌为引擎月窗面可验事实。 [证据: SHCOMP@2026-11-20, HSI@2026-11-20, SPX@2026-11-20]
  - E3 环3(叙事): 『全球商品脉冲→中国 PPI 回升→制造业名义盈利改善→A 股相对抗跌』整链为叙事层;引擎无中国行业盈利序列。 [证伪指标: CN_PPI_YOY]
- **机制链 M3-jpy-normalization**: 
  - E1 环1(观察,日本): JP_POLICY_RATE 三锚点 0.477→0.978→1.227,JP_CPI_YOY 2.99→1.97→2.44(先回落再回升),东京CPI 2026-09 回升至 2.69,JP_REAL_GDP_YOY 0.63→1.16 加速——『增长加速+通胀回升+持续加息』组合为点值面直接可验事实。 [证据: JP_POLICY_RATE@2026-10-01, JP_CPI_YOY@2026-10-01]
  - E1 环2(汇率): USDJPY 12个月 +1.49%(157.37→159.71,2025-11-21→2026-11-20 自配对原值)、自3个月前锚以来 +8.41%(147.32→159.71)——日本加息未能扭转日元弱势,与美国实际利率12个月 +102bp 的利差主导叙事相容。 [证据: USDJPY@2026-11-20, TIPS_10Y@2026-11-19]
  - E3 环3(叙事): 『日元贬值→输入通胀→支持继续加息』的正反馈为叙事层,引擎无日本进口价格序列;若日元大幅走强后日本通胀仍续升,输入通胀环被证伪。 [证伪指标: JP_CPI_YOY]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-tightening-persists**()
  - 情景: 基准情景(假设非预测): 假设美国通胀韧性延续、政策维持偏紧甚至再加码,实际利率高位震荡,高估值继续消化、波动中枢抬升。
  - 资产方向判断: 发达市场股票承压或高波动震荡,长久期高估值资产相对劣势;黄金与股票相关性不稳定(流动性压力时段同跌)。(置信: 有相关证据) 
  - 敏感变量: CPI, TIPS_10Y
  - 证伪指标: CPI 阈值 2027-01 CPI 同比回落至 2.8 以下且 CORE_PCE 同比回落至 2.8 以下(两者同时成立)则『通胀韧性』假设被证伪
  - 触发条件: FOMC 2026-12 或 2027-01 会议再度加息,或官方点阵图 2027 路径上移(时限 2027-02-05)
- **S2-inflation-cools**()
  - 情景: 反例情景(假设非预测): 假设核心通胀延续 2026-08 以来的回落(候选面 CORE_CPI 2026-05 2.82→2026-08 2.45),供给脉冲消退,政策转向观望甚至重新讨论降息,估值压力缓解。
  - 资产方向判断: 股票止跌回稳、波动回落,短久期与利率敏感资产相对受益;美元走强压力减弱。(置信: 有相关证据) 
  - 敏感变量: CORE_CPI, BEI_10Y
  - 证伪指标: CORE_CPI 阈值 2027-01 核心 CPI 同比回升至 2.8 以上,或 BEI_10Y 升破 2.6(任一成立)则『通胀快速回落』假设被证伪
  - 触发条件: FOMC 2026-12 会议声明移除进一步紧缩倾向,或 CORE_CPI 同比连续两个月低于 2.5(时限 2027-01-31)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

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
- [SKIP|—] S4_history_EA_REAL_GDP_YOY 地图计划指标 EA_REAL_GDP_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_EA_HICP_YOY 地图计划指标 EA_HICP_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
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

## 证据索引(68 行)

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
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:UST_5Y@2026-11-19 → UST_5Y
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:SHCOMP@2026-11-20 → SHCOMP
- snapshot_fact:HSI@2026-11-20 → HSI
- snapshot_fact:CN_LPR_1Y@2026-11-20 → CN_LPR_1Y
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-10-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2025-12-01 → EA_HICP_YOY
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
- s3_envelope:GBPUSD@2026-11-20 → GBPUSD
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
- s3_envelope:BTC@2026-11-19 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、EA_HICP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
