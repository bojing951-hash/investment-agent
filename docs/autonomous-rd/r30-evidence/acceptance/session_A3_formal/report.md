# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261121T144742Z @ 59dcc096fff5138429105214bbd24ccd3ce003bb
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 57/57 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-21、3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 8 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<130(日历期望261×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
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
- **CON-1**: 过去一年的全球主线是通胀中枢上移与货币政策再定价,而不是增长衰退: 增长面四地大体平稳——美国温和放缓(最新失业率 UNEMPLOYMENT 4.1)、欧元区与日本回升、中国低位修复。通胀面普遍上移: 中国生产端价格同比由负转正并明显走高(最新读数见走位面),欧元区消费通胀加速(读数见走位面),日本先回落再回升,美国消费与核心通胀同比中枢同样上移(引擎派生口径)。政策面分化而非同步紧缩: Fed 先降后升(目前有效联邦基金利率 DFF 3.88,一年净变动为零而方向已由降转升)。ECB 转入连续加息至 ECB_DFR 2.5。日本渐进收紧至 JP_POLICY_RATE 1.227。中国按兵不动并与欧美方向背离。
  - 依据: 证据面: 引擎三时点点值面与转折候选面(CPI、CORE_PCE、CN_PPI_YOY、CN_PMI_MFG、EA_HICP_YOY、JP_CPI_YOY、INDPRO、US_REAL_GDP、EA_REAL_GDP_YOY、JP_REAL_GDP_YOY、JP_POLICY_RATE),政策事件簇(POLCLUSTER-01 Fed 2025-12-10 降息;POLCLUSTER-02 ECB 2026-06-11 加息;POLCLUSTER-03 ECB 2026-09-10 与 Fed 2026-09-16 加息构成跨国同一事件簇)与点值面;三期对照与同比派生数值见 reader_map 各地区走位与机制链。
  - 竞争性解释1: 供给驱动解释: 若通胀上移主要由供给端(能源与运输瓶颈、行业供给侧整合)驱动,则其将随供给修复自行回落,政策无须持续紧缩——将观察到 BEI_10Y 与 BRENT_F 领先回落、核心通胀跟随下行。
  - 竞争性解释2: 需求过热解释: 若通胀上移由需求过热(财政扩张与工资-物价循环)驱动,则将具有黏性,政策须维持紧缩甚至加码——将观察到 CORE_PCE 增速持续高位且 UNEMPLOYMENT 维持低位。
  - 竞争性解释3: 巧合叠加解释: 若美欧中通胀同窗上移主要是各地基数与口径因素的巧合,则后续月份跨区相关性将减弱、各自独立波动。
  - 证据: CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01, JP_CPI_YOY@2026-10-01, CN_PMI_MFG@2026-10-01, INDPRO@2026-10-01
- **CON-2**: 美债长端利率升至高位而曲线更平、通胀预期温和: 最新 UST_10Y 5.04、UST_2Y 4.76、CURVE_2S10S 0.29、BEI_10Y 2.15、VIX 35.89——市场定价的是高利率与高波动的组合,通胀预期并未脱锚;TIPS_10Y 序列不可得,实际利率分量无法直接验证,名义上行的归因(实际利率 vs 期限溢价)在引擎面上不可裁决。
  - 依据: 证据面: 快照事实(见 evidence_refs)与 S4 序列月末口径复算(UST_10Y、UST_2Y、BEI_10Y、CURVE_2S10S,年度窗两端=2025-11 月末与 2026-11 月末,数值见机制链 CH-1 第 3 环);us_rates_trio 三利率共同交易日分解面 status=absent(TIPS_10Y 不可得,检索范围=快照 series_store 采集档通道)。
  - 竞争性解释1: 政策重定价解释: 若长端上行主要由政策再紧缩与增长韧性驱动,则短端应领先上行、曲线走平或持稳、BEI_10Y 温和——与当前组合(短端高位、曲线较一年前更平、盈亏平衡温和)相容。
  - 竞争性解释2: 期限溢价解释: 若长端上行主要由财政供给与期限溢价推升,则 BEI_10Y 应与名义利率同升、CURVE_2S10S 趋势陡峭化——当前盈亏平衡温和且曲线走平,与该解释的主方向不符,但尚不能排除财政因素的边际贡献。
  - 证据: UST_10Y@2026-11-19, UST_2Y@2026-11-19, BEI_10Y@2026-11-20, CURVE_2S10S@2026-11-20, VIX@2026-11-20
- **CON-3**: 近一月风险资产与黄金同步深跌、波动率翻倍、美元走强: SPX -10.92%、NIKKEI225 -12.67%、DAX -3.28%、SHCOMP -4.83%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20),UST_10Y 5.04 于同窗高位小幅回落(窗口 2026-10-21→2026-11-19);信用利差并未显著走阔(HY_OAS 3.52、IG_OAS 0.94),单月窗口不足以在「利率/贴现率驱动」与「增长担忧驱动」之间作出裁决。
  - 依据: 证据面: 引擎资产月窗复算(asset_moves 八行,窗口 2026-10-21→2026-11-20,UST_10Y 行至 2026-11-19,两端实测日随行),快照事实与信用利差对照(HY_OAS、IG_OAS、BB_OAS、B_OAS、CCC_OAS)。
  - 竞争性解释1: 贴现率驱动: 若压制来自高利率与波动冲击,则零票息的 GOLD_F 弹性应最大、DXY 偏强——与本月黄金回撤最深、美元走强的组合相容。
  - 竞争性解释2: 增长担忧驱动: 若回撤源于盈利预期下修,则 HY_OAS 走阔将领先或同步于股指、利率将因避险反而大幅下行——当前月窗信用利差变动温和、利率仅小幅回落,证据尚不足以支持该侧。
  - 竞争性解释3: 波动率自我强化: 若 VIX 冲高引发波动率目标与流动性反馈,则回撤与基本面指标的相关性将弱、修复也快——该解释与任何单一致因并列存在。
  - 证据: SPX@2026-11-20, NIKKEI225@2026-11-20, GOLD_F@2026-11-20, VIX@2026-11-20, DXY@2026-11-20, HY_OAS@2026-11-19
- **机制链 CH-1**: 全球通胀上移→政策再定价→利率高位与曲线走平→风险资产与黄金承压
  - E1 美中欧通胀于 2026-02→2026-05 同窗上移: 美国 CPI 同比(引擎派生口径)2.434→4.1666、中国 CN_PPI_YOY -0.9→3.9、欧元区 EA_HICP_YOY 1.9→3.2(引擎转折候选面,月频);美国 CORE_PCE 同比 2.85(2025-08 观测)→3.12(2026-09 观测)。 [证据: CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01]
  - E1 政策再定价跟进: ECB 于 2026-06-11、2026-09-10 各加息 25bp(ECB_DFR 2.0→2.5);Fed 于 2026-09-16 加息 25bp(DFEDTARU 3.75→4.0,与 ECB 决议构成跨国同一政策事件簇 POLCLUSTER-03);日本以无担保隔夜拆借月均口径渐进抬升(JP_POLICY_RATE 0.477→1.227);中国 CN_OMO_7D 1.4 与 CN_LPR_1Y 3.0 按兵不动(政策背离端)。 [证据: ECB_DFR@2026-09-16, ECB_MRO@2026-09-16, JP_POLICY_RATE@2026-10-01]
  - E2 长端利率升至高位而曲线走平: UST_10Y 4.02→5.04、UST_2Y 3.47→4.76(2025-11-28→2026-11-19 月末口径),CURVE_2S10S 0.55→0.29,BEI_10Y 2.23→2.15(通胀预期温和)。 [缺失环: 缺失环【假设】: 政策利率→长端利率的映射为假设——本引擎 TIPS_10Y 序列不可得(三利率共同交易日分解缺席),实际利率与期限溢价的分解无法直接验证,仅能以短端大幅上行+曲线走平+盈亏平衡温和间接支持政策驱动一侧。]
  - E3 高利率与波动冲击压制风险资产与非孳息资产: 近一月 SPX -10.92%、NIKKEI225 -12.67%、DAX -3.28%、SHCOMP -4.83%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20)。 [证伪指标: VIX]
- **机制链 CH-2**: 中国再通胀与欧美再紧缩的政策背离通道(并列竞争通道)
  - E1 中国生产端价格由通缩转再通胀: CN_PPI_YOY -2.1(2025-10)→-0.9(2026-02)→3.9(2026-05)→5.7(2026-10);制造业 PMI 同比(派生)-2.2→-0.2→+0.61 转正。 [证据: CN_PMI_MFG@2026-10-01]
  - E2 中国政策未随再通胀收紧: CN_OMO_7D 1.4 三期持稳、CN_LPR_1Y 3.0 持稳,2026-11-02 起政策利率锚换为隔夜逆回购利率(CN_POLICY_OVERNIGHT 1.25)——与 ECB(2026-06 起)与 Fed(2026-09)的加息方向相反。 [缺失环: 缺失环【假设】: 换锚与不收紧的动机(以再通胀修复名义增长/汇率考量)为假设——引擎无央行沟通文本序列,该环不可验证。]
  - E3 背离的资产含义: 中国资产本月相对抗跌(SHCOMP 月窗 -4.83% vs SPX -10.92%),但单月窗口不足以把「政策背离红利」与「估值/结构因素」区分开。 [证伪指标: USDCNY]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-再紧缩延续**(基准(主解释延续))
  - 情景: 假设(非预测): 通胀中枢上移与政策再紧缩延续,长端利率维持高位,增长温和降温但不衰退,高波动逐步消化而非扩散为信用事件。
  - 资产方向判断: 长久期成长股指(SPX/NDX)与黄金(GOLD_F)承压、VIX 中枢抬升、DXY 偏强;现金与短久期相对占优。注意历史相似样本 2022-06 锚后 12 个月 SPX +17.57%——紧缩中段风险资产亦可先深跌后收复,方向判断置信有限。(置信: 有相关证据) 
  - 敏感变量: BEI_10Y, VIX
  - 证伪指标: VIX 阈值 VIX 月末值自 2026-11 的 35.89 回落至 20 下方并连续两个月维持(波动冲击趋势性消退即推翻本情景主通道)
  - 触发条件: BEI_10Y 月末维持在 2.2 附近或以下(通胀预期未脱锚)且 Fed 或 ECB 再加息一次或点阵图上修(时限 2027-05-21)
- **S2-通胀快速回落→宽松重定价**(反例(与基准并列检验))
  - 情景: 假设(非预测): 通胀回落速度快于政策反应,市场转向宽松定价,结构上类似 2025-03 锚点之后的路径(该锚点后 12 个月 DFEDTARU -0.75pp、SPX +16.33%、GOLD_F +48.83%)。
  - 资产方向判断: 股指与黄金反弹、DXY 走弱、VIX 回落(历史相似样本 2025-03 锚后 12 个月 SPX +16.33%、黄金期货 +48.83%)。(置信: 有历史相似证据) 
  - 敏感变量: CPI, BEI_10Y
  - 证伪指标: BEI_10Y 阈值 BEI_10Y 月末升破 2.60 并连续两个月维持(通胀预期脱锚上行,宽松重定价前提失效)
  - 触发条件: CPI 同比(引擎派生口径)连续两个月回落,且 Fed 在 2026-09 加息后按兵不动超过两个会议周期(时限 2027-05-21)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2022-06 | 0.888098 | 0.0 | volatility 37.2%、valuation 29.0% |
| 2 | 2025-03 | 0.967636 | 4.1096 | volatility 73.7%、rates 15.7% |
| 3 | 2020-10 | 0.979606 | 8.2192 | rates 78.6%、valuation 9.9% |
| 4 | 2023-10 | 1.343214 | 52.0548 | volatility 74.6%、valuation 14.1% |
| 5 | 2019-10 | 1.614863 | 94.5205 | volatility 49.0%、rates 22.6% |

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
- [OK |语义✔] S4_history_EA_REAL_GDP_YOY 
- [OK |语义✔] S4_history_EA_HICP_YOY 
- [OK |语义✔] S4_history_ECB_MRO 
- [OK |语义✔] S4_history_ECB_DFR 
- [OK |语义✔] S4_history_JP_REAL_GDP_YOY 
- [OK |语义✔] S4_history_JP_CPI_YOY 
- [OK |语义✔] S4_history_JP_CPI_TOKYO_YOY 
- [OK |语义✔] S4_history_JP_POLICY_RATE 
- [OK |语义✔] S4_history_UST_10Y 
- [FAIL|语义✗] S4_history_TIPS_10Y 
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
- [OK |语义✔] S5_compare 命中 49 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,DFEDTARU,DFF,CN_PMI_MFG,CN_CPI_YOY,CN_PPI_YOY,CN_POLICY_OVERNIGHT,CN_OMO_7D,CN_LPR_1Y,EA_REAL_GDP_YOY,EA_HICP_YOY,ECB_MRO,ECB_DFR,JP_REAL_GDP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(64 行)

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
- s3_envelope:BTC@2026-11-20 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
