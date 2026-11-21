# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261120T142412Z @ 2953c29
- 快照: research_snapshot_20261120 (target 20261120)
- 数据门(gate_a): 60/60 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-20、3个月前@2026-08-20、最新一期@2026-11-20 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 9 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: DFEDTARU(缺什么: DFEDTARU(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<131(日历期望262×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 7175.83 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-19]
- NDX = 26517.05 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-19]
- RUT = 2655.11 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-19]
- DXY = 103.94 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-19]
- EURUSD = 1.1 usd_per_eur @2026-11-19 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-19]
- GOLD_F = 3627.9 usd_per_oz @2026-11-19 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-19]
- SILVER_F = 42.83 usd_per_oz @2026-11-19 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-19]
- BRENT_F = 90.05 usd_per_barrel @2026-11-19 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-19]
- VIX = 28.44 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-19]
- DAX = 25736.24 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-18]
- CAC40 = 8146.83 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-18]
- USDJPY = 159.61 jpy_per_usd @2026-11-19 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-19]
- USDCNY = 6.67 cny_per_usd @2026-11-19 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-19]
- HY_OAS = 3.47 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-18]
- BB_OAS = 2.05 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-18]
- B_OAS = 3.73 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-18]
- CCC_OAS = 13.53 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-18]
- IG_OAS = 0.93 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-18]
- UST_2Y = 4.8 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-11-18]
- UST_10Y = 5.07 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-18]
- UST_30Y = 5.41 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_30Y@2026-11-18]
- TIPS_5Y = 2.66 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:TIPS_5Y@2026-11-18]
- TIPS_10Y = 2.88 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:TIPS_10Y@2026-11-18]
- BEI_5Y = 2.22 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:BEI_5Y@2026-11-19]
- BEI_10Y = 2.16 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-19]
- CURVE_2S10S = 0.28 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-11-19]
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- UST_5Y = 4.89 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-18]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- SHCOMP = 3533.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-20]
- HSI = 22410.8 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-20]
- CN_LPR_1Y = 3.0 percent @2026-11-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-11-20]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- DFF = 3.88 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:DFF@2026-11-18]
- DFEDTARU = 4.0 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:DFEDTARU@2026-11-19]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- JP_CPI_YOY = 2.44 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-10-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1**: 过去一年美欧中三地通胀在相近统计月内同步再加速,而日本先经历通胀下行后再回升;该同步性是共同全球冲击(上游成本或需求)的结果,还是各地独立通胀过程在相近月份的共振,现有月频证据不能裁决先后与因果。
  - 依据: 引擎转折候选面显示美CPI、欧HICP、中PPI的最大三个月变动窗同为二月至五月;月度序列显示中PPI与欧HICP均在三月观测出现首个台阶。按统计期对齐,不代表当时市场信息集(research_mode_gate: event_study blocked)。
  - 竞争性解释1: 共同全球冲击:上游生产者价格(中PPI自通缩区间快速转正)若持续领行并伴随美欧核心通胀跟随,支持商品/成本冲击的全球传导【假设,E2】
  - 竞争性解释2: 独立过程共振:若后续各国通胀脱钩(有的回落有的续升)且核心通胀不跟随,则同期抬升更可能是巧合共振与基数效应(月度同比对上年同期基数敏感)【假设,E2】
  - 竞争性解释3: 统计口径因素:美国2025年停摆后的补发布批次造成序列节奏扰动,可能放大了表观同步性【假设,尚未验证】
  - 证据: CPI@2026-10-01, EA_HICP_YOY@2026-10-01, CN_PMI_MFG@2026-10-01, CORE_CPI@2026-10-01
- **C2**: 最近一个月全球风险资产普遍回调且波动率急升,日经225幅度最大;其驱动存在三种数据同样容纳的解释——实际利率上行与高估值压缩渠道、日元套息平仓渠道、增长恐慌渠道。汇率与利率分解证据当前更容许第一种,但不能闭合裁决。
  - 依据: 引擎资产月窗与归档传导边:黄金与实际利率长窗共动为负且黄金近月幅度居前,而USDJPY同窗不降反升,与套息平仓渠道的汇率预测方向相反;实际利率十二个月窗大幅上行,与增长恐慌渠道的实际利率预测方向相反。
  - 竞争性解释1: 实际利率/估值渠道:若主因是实际利率上行压缩估值与无现金流资产,则回调应集中在高估值权益与黄金,且USDJPY无系统性下行(归档边USDJPY-UST10Y与VIX-USDJPY均近零)【推断,有相关证据】
  - 竞争性解释2: 日元套息平仓渠道:若BOJ连续收紧引发套息头寸回补,则USDJPY应显著下行(日元升值)且先于或同步于日经回调——实测方向相反,该渠道被当前窗口数据反驳,但月频/日频混合证据不能排除局部时点的短期作用【假设,E3】
  - 竞争性解释3: 增长恐慌渠道:若市场定价增长失速,则实际利率与盈亏平衡通胀率应同向下行、就业指标应恶化——实测实际利率仍处高位、失业率下行,该渠道证据不足【推断】
  - 证据: TIPS_10Y@2026-11-18, VIX@2026-11-19, USDJPY@2026-11-19, NIKKEI225@2026-11-20, GOLD_F@2026-11-19
- **C3**: 中国货币政策全年按兵不动并于2026年11月切换操作锚,与美欧日的再收紧形成分化;这是低通胀环境给予的政策空间的被动结果,还是稳增长诉求下的主动选择,月频证据不能裁决,且两种解释对后续的预测不同。
  - 依据: 中国CPI同比远低于美欧,通胀环境差异客观存在;同时中国PMI仍低于荣枯线,增长诉求也客观存在——两个事实分别支持两种解释,不可偏废。
  - 竞争性解释1: 通胀差异的被动结果:若中国CPI与PPI持续上行并传导至终端,政策空间将收窄,届时若仍不收紧,则该解释被削弱【推断】
  - 竞争性解释2: 稳增长的主动选择:若通胀维持低位而增长指标改善,按兵不动可解释为主动留白;若增长继续走弱且政策仍不动,则需引入其他约束(汇率/杠杆)解释【推断】
  - 证据: ECB_DFR@2026-09-16, DFF@2026-11-18, CN_LPR_1Y@2026-11-20, JP_POLICY_RATE@2026-10-01, CN_PMI_MFG@2026-10-01
- **机制链 M1**: 
  - E1 【事实/E1】通胀再加速:美CPI同比自2026-02的2.434升至2026-05的4.1666(引擎候选面窗端点);欧HICP同期1.9→3.2;中PPI同期-0.9→3.9并于2026-03转正(-0.9→0.5→2.8→3.9,引擎月度序列);最近有效美CPI同比3.72(2026-09观测),核心PCE同比2.85→3.04→3.12(引擎派生)。 [证据: CPI@2026-10-01, EA_HICP_YOY@2026-10-01, CN_PMI_MFG@2026-10-01, CORE_PCE@2026-09-01]
  - E1 【事实/E1】政策响应路径:BOJ无担保隔夜拆借月均0.477→1.227(12个月净+67bp,2025-12起六次上行);ECB存款便利利率2026-06-11与2026-09-10两次决议各+25bp至2.5(MRO至2.65);Fed有效联邦基金利率2025-12-11 -25bp(3.89→3.64)后2026-09-17 +25bp至3.88;中国7天逆回购1.4与LPR 3.0全年未动,2026-11-02操作锚换为隔夜1.25。 [证据: JP_POLICY_RATE@2026-10-01, ECB_DFR@2026-09-16, DFF@2026-11-18, CN_LPR_1Y@2026-11-20]
  - E2 【假设/E2】因果环『通胀促使央行收紧』:归档传导边COREPCE-FEDFUNDS历史共动r=0.422(n=118,月网格)支持通胀与政策的共动关系,但不判因果;引擎无央行反应函数与决议叙事序列,决议动机归因此环为假设。 [缺失环: 引擎无央行反应函数/决议理由序列,『通胀→收紧』的动机环为【假设】;可验证部分仅为两端序列的共动(E1)。]
  - E1 【事实/E1】利率市场定价:12个月共同交易日窗UST_10Y +95bp = TIPS_10Y +103bp + BEI_10Y -8bp(恒等残差0);近1月窗名义-8bp=实际+8bp+盈亏平衡-16bp;归档边TIPS10Y-UST10Y共动r=0.8278(n=2495)——债市上行几乎全部在实际利率,通胀预期未跟随通胀读数(归档边CPI-BEI10Y r=0.1733弱)。 [证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19]
  - E1 【事实/E1】实际利率→黄金:归档边TIPS10Y-GOLD_F r=-0.3013(n=2491,全窗);GOLD_F 12个月窗-11.14%(4082.8→3627.9)、近1月窗-12.42%(4142.6→3627.9)。 [证据: GOLD_F@2026-11-19, TIPS_10Y@2026-11-18]
  - E2 【假设/E2】实际利率→权益估值压缩:市场内环VIX-SPX r=-0.7138(roll60末-0.9176)与SPX-HY_OAS r=-0.6318为E1共动;但利率→权益直接边近零(NDX-UST10Y r=0.0586),且当前SPX_CAPE z=2.82处历史高位——『实际利率压制高估值』这一环为假设,引擎无估值贴现率/风险偏好代理序列。 [缺失环: 利率→权益的直接传导环在归档边为近零,权益回调经由估值/波动/信用内环的归因为【假设】;缺失环节=风险偏好或估值贴现序列。]
- **机制链 M2**: 
  - E1 【事实/E1】美日政策分化:BOJ隔夜月均+67bp至1.227,而Fed先降后升(DFF 3.63@2026-08-19→3.88@2026-11-18);日经225近1月-11.92%为引擎资产月窗中幅度最大。 [证据: JP_POLICY_RATE@2026-10-01, DFF@2026-11-18, NIKKEI225@2026-11-20]
  - E1 【事实/E1】汇率证据反向:USDJPY近1月+1.14%(157.806→159.610)、12个月+2.61%(155.548→159.610)——日元未升值;归档边USDJPY-UST10Y r=0.0313、USDJPY-UST2Y r=0.0064、VIX-USDJPY r=-0.0238均近零。 [证据: USDJPY@2026-11-19]
  - E3 【假设/E3】套息平仓→日经领跌→全球传染:若此链主导,USDJPY应显著下行(如近1月窗-5%量级)且利差收窄先于日经回调;实测汇率方向相反,该链在当前窗口被数据反驳,但不排除局部时点短期作用。 [证伪指标: USDJPY]
- **机制链 M3**: 
  - E1 【事实/E1】波动事实:VIX近1月17.31→28.44(+64.3%),SPX -6.96%,风险偏好显著恶化。 [证据: VIX@2026-11-19, SPX@2026-11-19]
  - E1 【事实/E1】增长面未恶化:失业率4.4→4.1→4.1(2025-09→2026-07→2026-10观测),工业生产同比1.19→1.25→2.15(引擎派生),实际GDP同比2.42→2.19→2.07为温和放缓而非失速;归档边INDPRO-SPX r=-0.0471近零。 [证据: UNEMPLOYMENT@2026-10-01, INDPRO@2026-10-01]
  - E3 【假设/E3】若增长恐慌主导定价,实际利率与盈亏平衡应同向下行、就业应恶化;实测实际利率12个月+103bp仍向上、失业率下行,方向不符,该链证据不足。 [证伪指标: TIPS_10Y]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-1**()
  - 情景: 【假设非预测】基准情景:若通胀再加速延续(最近有效美CPI同比3.72的基础上维持3.5%上方)且BOJ/ECB维持紧缩姿态、Fed不再转向,实际利率(TIPS_10Y)维持高位
  - 资产方向判断: 高估值权益与黄金等对实际利率敏感的资产继续承压,波动率维持高位,美元相对多数非美货币偏强(置信: 有相关证据) 
  - 敏感变量: TIPS_10Y, CPI
  - 证伪指标: CPI 阈值 2027-01-31前最近有效美CPI同比回落至3.0%下方,则本情景的通胀延续前提被证伪(当前最近有效值3.72,2026-09观测)
  - 触发条件: 2026-12与2027-01发布的美国CPI同比均≥3.5%,且TIPS_10Y维持≥2.75(时限 2027-01-31)
- **SCN-2**()
  - 情景: 【假设非预测】反例情景:若美国通胀回落(CPI同比降至3.0%下方)且Fed不再加息、ECB停止加息,实际利率自高位回落
  - 资产方向判断: 权益修复、黄金反弹、波动率回落——历史相似段(TOP-5独立簇)事后6与12个月黄金全为正、事后12个月SPX全为正(符号一致率1.0;相似≠因果≠预测,事后块仅为历史记录)(置信: 有历史相似证据) 
  - 敏感变量: CPI, TIPS_10Y
  - 证伪指标: CPI 阈值 2027-02-28前最近有效美CPI同比持续≥3.5%,或ECB再加息使DFR高于2.5,则本情景被证伪
  - 触发条件: 最近有效美国CPI同比≤3.0,且TIPS_10Y较2026-11-18的2.88回落至少25bp(≤2.63)(时限 2027-02-28)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.673446 | 0.0 | rates 48.5%、volatility 32.3% |
| 2 | 2022-06 | 0.794208 | 1.3699 | rates 50.8%、valuation 33.4% |
| 3 | 2023-10 | 0.968894 | 26.0274 | volatility 53.4%、valuation 25.1% |
| 4 | 2021-02 | 1.203292 | 69.863 | rates 82.8%、inflation 8.5% |
| 5 | 2019-12 | 1.280722 | 72.6027 | rates 47.1%、volatility 39.1% |

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
- [SKIP|—] S4_history_DFEDTARU 地图计划指标 DFEDTARU 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
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

## 证据索引(70 行)

- snapshot_fact:SPX@2026-11-19 → SPX
- snapshot_fact:NDX@2026-11-19 → NDX
- snapshot_fact:RUT@2026-11-19 → RUT
- snapshot_fact:DXY@2026-11-19 → DXY
- snapshot_fact:EURUSD@2026-11-19 → EURUSD
- snapshot_fact:GOLD_F@2026-11-19 → GOLD_F
- snapshot_fact:SILVER_F@2026-11-19 → SILVER_F
- snapshot_fact:BRENT_F@2026-11-19 → BRENT_F
- snapshot_fact:VIX@2026-11-19 → VIX
- snapshot_fact:DAX@2026-11-18 → DAX
- snapshot_fact:CAC40@2026-11-18 → CAC40
- snapshot_fact:USDJPY@2026-11-19 → USDJPY
- snapshot_fact:USDCNY@2026-11-19 → USDCNY
- snapshot_fact:HY_OAS@2026-11-18 → HY_OAS
- snapshot_fact:BB_OAS@2026-11-18 → BB_OAS
- snapshot_fact:B_OAS@2026-11-18 → B_OAS
- snapshot_fact:CCC_OAS@2026-11-18 → CCC_OAS
- snapshot_fact:IG_OAS@2026-11-18 → IG_OAS
- snapshot_fact:UST_2Y@2026-11-18 → UST_2Y
- snapshot_fact:UST_10Y@2026-11-18 → UST_10Y
- snapshot_fact:UST_30Y@2026-11-18 → UST_30Y
- snapshot_fact:TIPS_5Y@2026-11-18 → TIPS_5Y
- snapshot_fact:TIPS_10Y@2026-11-18 → TIPS_10Y
- snapshot_fact:BEI_5Y@2026-11-19 → BEI_5Y
- snapshot_fact:BEI_10Y@2026-11-19 → BEI_10Y
- snapshot_fact:CURVE_2S10S@2026-11-19 → CURVE_2S10S
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:UST_5Y@2026-11-18 → UST_5Y
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:SHCOMP@2026-11-20 → SHCOMP
- snapshot_fact:HSI@2026-11-20 → HSI
- snapshot_fact:CN_LPR_1Y@2026-11-20 → CN_LPR_1Y
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:DFF@2026-11-18 → DFF
- snapshot_fact:DFEDTARU@2026-11-19 → DFEDTARU
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-10-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-20 → SZCI
- s3_envelope:CHINEXT@2026-11-20 → CHINEXT
- s3_envelope:HSCEI@2026-11-20 → HSCEI
- s3_envelope:NVDA@2026-11-19 → NVDA
- s3_envelope:AAPL@2026-11-19 → AAPL
- s3_envelope:MSFT@2026-11-19 → MSFT
- s3_envelope:TLT@2026-11-19 → TLT
- s3_envelope:IEF@2026-11-19 → IEF
- s3_envelope:SHY@2026-11-19 → SHY
- s3_envelope:HYG@2026-11-19 → HYG
- s3_envelope:LQD@2026-11-19 → LQD
- s3_envelope:GBPUSD@2026-11-19 → GBPUSD
- s3_envelope:WTI_F@2026-11-19 → WTI_F
- s3_envelope:GLD@2026-11-19 → GLD
- s3_envelope:USO@2026-11-19 → USO
- s3_envelope:EEM@2026-11-19 → EEM
- s3_envelope:EZU@2026-11-19 → EZU
- s3_envelope:FEZ@2026-11-19 → FEZ
- s3_envelope:EWU@2026-11-19 → EWU
- s3_envelope:EWG@2026-11-19 → EWG
- s3_envelope:EWJ@2026-11-19 → EWJ
- s3_envelope:INDA@2026-11-19 → INDA
- s3_envelope:FXI@2026-11-19 → FXI
- s3_envelope:BTC@2026-11-18 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-18 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、DFEDTARU、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
