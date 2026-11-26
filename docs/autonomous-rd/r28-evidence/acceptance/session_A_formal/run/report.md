# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261121T074401Z @ 48c03cb847ff985615c4f2254558d3a7f0be4b1a
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 60/60 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-21、3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 8 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<130(日历期望261×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
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
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CON-1**: 过去一年的全球主线是通胀中枢上移与货币政策再定价,而不是增长衰退: 四地增长大体平稳(美国温和放缓、日本回升、中国低位修复、欧元区增长维数据不可得),而通胀同比普遍上移(美欧生产与消费价格走高、中国生产端由通缩转再通胀、日本先回落再回升);政策取向上 Fed 先降后升一年净变动为零、ECB 最先转入连续加息、日本以市场口径渐进收紧、中国按兵不动并更换政策利率锚——政策与通胀的组合在四地分化,而非同步紧缩。近一月叠加急剧的波动冲击(VIX 翻倍、四地股指与黄金深回撤),把「通胀-政策」主线推向「增长担忧」的检验。
  - 依据: 证据面: 引擎三时点点值面与转折候选面(CPI、CORE_PCE、CN_PPI_YOY、CN_PMI_MFG、EA_HICP_YOY、JP_CPI_YOY、INDPRO、US_REAL_GDP、JP_REAL_GDP_YOY、JP_POLICY_RATE),政策事件簇与点值面(DFEDTARU、DFF、ECB_DFR、ECB_MRO、央行七天逆回购利率、隔夜新锚、LPR 报价利率),资产月窗面(SPX、NIKKEI225、GOLD_F、VIX)。
  - 竞争性解释1: 供给驱动解释: 若通胀上移主要由供给端(能源与运输瓶颈、行业供给侧整合)驱动,则其将随供给修复自行回落,政策无须持续紧缩——将观察到 BEI_10Y 与大宗价格领先回落、核心通胀跟随下行。
  - 竞争性解释2: 需求过热解释: 若通胀上移由需求过热(财政扩张与工资-物价循环)驱动,则将具有黏性,政策须维持紧缩甚至加码——将观察到 CORE_PCE 增速持续高于目标且 UNEMPLOYMENT 维持低位。
  - 竞争性解释3: 巧合叠加解释: 若美欧中通胀同窗上移主要是各地基数与口径因素的巧合,则后续月份跨区相关性将减弱、各自独立波动。
  - 证据: CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01, JP_CPI_YOY@2026-10-01, CN_PMI_MFG@2026-10-01, INDPRO@2026-10-01
- **CON-2**: 十年期美债名义利率的过去一年上行几乎全部由实际利率承载,盈亏平衡通胀率反而小幅回落(年度窗 +91bp = 实际 +102bp + 盈亏平衡 -11bp);近 30 日窗名义 -8bp = 实际 +11bp + 盈亏平衡 -19bp,通胀预期加速回落。同期短端大幅上行(UST_2Y 升至 4.76)、曲线走平(CURVE_2S10S 至 0.29)——市场定价的是「实际利率型」再紧缩与通胀预期回落并存,而非通胀预期脱锚,也与期限溢价主导的形态(陡峭化)不符。
  - 依据: 证据面: 引擎共同交易日三利率分解(年度窗 2025-11-19→2026-11-19、30 日窗 2026-10-20→2026-11-19;快照事实见 evidence_refs),曲线与短端快照事实。
  - 竞争性解释1: 期限溢价解释: 若长端上行主要来自财政供给与期限溢价,则 BEI_10Y 将与名义利率同升、CURVE_2S10S 将趋势性陡峭化——年度窗盈亏平衡回落 11bp 且近三月曲线走平,与该解释的主方向不符,但尚不能排除财政因素的边际贡献。
  - 竞争性解释2: 自然利率解释: 若实际利率上行源于增长预期改善推升自然利率,则风险资产将与实际利率同涨——而近一月 SPX 深回撤与 TIPS_10Y 上行反向,与该解释不相容(窗口尚短,不能定论)。
  - 证据: UST_10Y@2026-11-19, TIPS_10Y@2026-11-19, BEI_10Y@2026-11-20, CURVE_2S10S@2026-11-20, SPX@2026-11-20
- **CON-3**: 近一月风险资产与黄金深回撤、波动率翻倍、美元走强,高收益利差 HY_OAS 已走阔至 3.52(2026-11-19 观测),较 2026-08 月末明显走阔——方向上与实际利率上行一致(黄金的零票息属性对实际利率弹性最大,回撤也最深);但 HY_OAS 走阔与长端名义利率近 30 日小幅回落同时出现,单月窗口不足以在「政策/实际利率驱动」与「增长担忧驱动」之间作出裁决。
  - 依据: 证据面: 引擎资产月窗复算(SPX、NIKKEI225、GOLD_F、VIX、DAX、DXY、SHCOMP)、TIPS_10Y 30 日窗复算、HY_OAS 月末序列(2026-08 末以来连续走阔)。
  - 竞争性解释1: 实际利率驱动: 若压制来自贴现率上行,则零票息的 GOLD_F 对 TIPS_10Y 的弹性应最大、DXY 偏强——与本月黄金回撤最深、美元走强的组合相容。
  - 竞争性解释2: 增长担忧驱动: 若回撤源于盈利预期下修,则 HY_OAS 走阔将领先或同步于股指、利率将因避险反而下行——本月 HY_OAS 已明显走阔、名义长端 30 日窗回落 8bp,证据开始支持该侧。
  - 竞争性解释3: 流动性/去杠杆冲击: 黄金与 VIX 的同向急跌急升并存亦与保证金去杠杆或流动性螺旋相容——该解释下多个资产同向抛售与波动率急升并现,数据同样容纳,区分须待回购或美元融资面指标(本引擎无该序列,此环为【假设】)。
  - 证据: SPX@2026-11-20, GOLD_F@2026-11-20, VIX@2026-11-20, DXY@2026-11-20, HY_OAS@2026-11-19, TIPS_10Y@2026-11-19
- **机制链 CH-1**: 全球通胀上移→政策再定价→实际利率上行→风险资产与黄金承压、波动与信用压力抬升
  - E1 美中欧通胀于 2026-02→2026-05 同窗上移: 美国CPI同比 2.434→4.1666、中国 CN_PPI_YOY 同比 -0.9→3.9、欧元区 EA_HICP_YOY 同比 1.9→3.2(引擎转折候选面,月频);美国 CORE_PCE 同比由 2.85(2025-08 观测)升至 3.12(2026-09 观测)。 [证据: CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01]
  - E1 政策再定价跟进: ECB 于 2026-06-11、2026-09-10 各加息 25bp(ECB_DFR 2.0→2.5);Fed 于 2026-09-16 加息 25bp(DFEDTARU 3.75→4.0,与 ECB 9 月决议构成跨国同一政策事件簇);日本以无担保隔夜拆借月均口径渐进抬升(JP_POLICY_RATE 0.477→1.227);中国 CN_OMO_7D 1.4 与 CN_LPR_1Y 3.0 按兵不动(政策背离端)。 [证据: ECB_DFR@2026-09-16, ECB_MRO@2026-09-16, JP_POLICY_RATE@2026-10-01]
  - E2 美债长端名义利率上行几乎全部由实际利率承载: 年度窗 UST_10Y +91bp = TIPS_10Y +102bp + BEI_10Y -11bp(2025-11-19→2026-11-19 共同交易日复算);30 日窗名义 -8bp = 实际 +11bp + 盈亏平衡 -19bp(2026-10-20→2026-11-19);同期短端上行快于长端、曲线走平。 [缺失环: 缺失环【假设】: 政策利率→长端实际利率的映射为假设——引擎面无远期政策曲线或期限溢价分解的直接观测,仅能以 TIPS_10Y 与政策决议窗口的同向变动、以及短端与曲线的联动间接支持。]
  - E3 高实际利率对风险资产与非孳息资产估值形成压制,并与增长担忧叠加: 近一月 SPX -10.92%、NIKKEI225 -12.67%、GOLD_F -15.29%、SHCOMP -4.83%、DAX -3.28%、VIX +115.17%、DXY +1.99%(月窗复算,两端观测日随行披露);HY_OAS 自 2026-08 末走阔至 3.52。 [证伪指标: TIPS_10Y]
- **机制链 CH-2**: 美国增长温和降温→政策两难(与通胀主链并列的竞争通道)
  - E1 美国增长面: 实际GDP同比 2.42(2025Q2)→2.19(2026Q2)→2.07(2026Q3,事后回顾口径);失业率 4.4→4.1→4.1;INDPRO 同比 1.19→1.25→2.15(先于 2026-02 一度降至 0.7972 后回升)。 [证据: US_REAL_GDP@2026-07-01, UNEMPLOYMENT@2026-10-01, INDPRO@2026-10-01]
  - E3 增长温和降温与通胀上移并存使政策进入两难: 若增长进一步走弱而通胀居高,则紧缩的可持续性存疑——近一月 HY_OAS 走阔与 BEI_10Y 回落(-19bp/30日)并现,提示增长担忧已进入定价;该环为叙事推断,非引擎直接可验证。 [证伪指标: UNEMPLOYMENT]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-紧缩延续与波动高企**(基准(主解释延续))
  - 情景: 假设(非预测): 通胀中枢上移与政策再紧缩延续,实际利率维持高位甚至进一步上行,增长温和降温但不衰退,波动与信用压力维持高位。
  - 资产方向判断: 长久期成长股指(SPX/NDX)与黄金(GOLD_F)承压、VIX 中枢维持高位、DXY 偏强、HY_OAS 维持走阔后的高位;现金与短久期相对占优。(置信: 有相关证据) 
  - 敏感变量: TIPS_10Y, BEI_10Y
  - 证伪指标: TIPS_10Y 阈值 TIPS_10Y 月末值自 2026-11 的 2.88 回落至 2.50 下方并连续两个月维持(实际利率趋势性下行即推翻本情景主通道)
  - 触发条件: BEI_10Y 月末维持在 2.2 附近或以下(名义上行继续由实际利率承载)且 Fed 再加息一次或点阵图上修(时限 2027-05-21)
- **S2-通胀快速回落→宽松重定价**(反例(与基准并列检验))
  - 情景: 假设(非预测): 通胀回落速度快于政策反应,市场转向宽松定价,重演 2023-10 锚点之后利率见顶回落、风险资产与黄金上行的历史相似路径。
  - 资产方向判断: 股指与黄金反弹、DXY 走弱、VIX 回落(历史相似样本 2023-10 锚后 12 个月 SPX +36.04%、黄金期货 +37.86%,月末口径)。(置信: 有历史相似证据) 
  - 敏感变量: BEI_10Y, CPI
  - 证伪指标: BEI_10Y 阈值 BEI_10Y 月末升破 2.60 并连续两个月维持(通胀预期脱锚上行,宽松重定价前提失效)
  - 触发条件: CPI 同比(引擎派生口径)连续两个月回落,且 Fed 在最后一次加息后按兵不动超过两个会议周期(时限 2027-05-21)

## 语义审查(席位已裁)

- 席位裁决: REVISE(档: audit/semantic_review/20261121/VERDICT-20261121T074401Z-02.json)

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

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
