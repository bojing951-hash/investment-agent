# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261120T162144Z @ 2953c29
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 58/58 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-21、3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 10 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: DFEDTARU(缺什么: DFEDTARU(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<130(日历期望261×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_HICP_YOY(缺什么: EA_HICP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

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
- EA_HICP_YOY = 1.9 percent @2025-12-01 [质量:DEGRADED] [来源:snapshot_fact:EA_HICP_YOY@2025-12-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1**: 过去一年全球风险资产普跌与美元走强的主导渠道,证据面容纳两种并列解释:其一,再通胀→政策再收紧→实际利率抬升→折现率冲击,压制长久期权益与无息资产黄金;其二,日本货币政策正常化→套息头寸平仓→波动全球传染。两个可核面对前者更有利:USDJPY近月不跌反微升,与套息平仓应有的日元急升特征相反;HY_OAS信用利差未走阔,与信用收缩型下跌不符。但日经225跌幅大于SPX的放大项仍可能含日本自身因素,竞争解释不能完全排除。
  - 依据: TIPS_10Y一年显著上行而BEI_10Y基本持平略降,十年期美债UST_10Y长端抬升由实际利率主导(共同交易日分解);近一月SPX与NIKKEI225和GOLD_F下跌,VIX与DXY上行;USDJPY微升;HY_OAS处于较窄水平而CCC_OAS偏高。证据引用: TIPS_10Y/BEI_10Y/UST_10Y/SPX/NIKKEI225/GOLD_F/VIX/DXY/USDJPY/HY_OAS快照事实。
  - 竞争性解释1: 主解释(再通胀-折现率渠道):若实际利率TIPS_10Y维持高位,折现率冲击将持续压制SPX与GOLD_F等长久期/无息资产,DXY随利差走强——与近一月观察一致
  - 竞争性解释2: 竞争解释A(日本套息平仓渠道):若日央行正常化引发融资头寸去杠杆,USDJPY应显著下行(日元急升)且日经领跌全球——汇率面观察与此不符,但权益放大项不可全排除
  - 竞争性解释3: 竞争解释B(高估值去化渠道):若CAPE高位下的利率敏感性放大回调,则跌幅应集中于高估值指数而信用面平稳——与HY_OAS未走阔相容,可与主解释叠加而非互斥
  - 证据: TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19, UST_10Y@2026-11-18, SPX@2026-11-19, NIKKEI225@2026-11-20, GOLD_F@2026-11-19, VIX@2026-11-19, DXY@2026-11-19, USDJPY@2026-11-19, HY_OAS@2026-11-18
- **C2**: 中国PPI同比由负转正并大幅走高,而中国CPI同比温和、制造业PMI三个对照锚水平均处荣枯线下方:供给侧/上游成本推动、内需边际修复、低基数效应三种解释并存,引擎无行业成分与进口价格序列,不能裁决。CN_PMI_MFG同比维度同期改善为需求侧解释提供部分支持,但其水平仍在收缩区间,支持力度有限。
  - 依据: CN_PMI_MFG三锚水平低于五十;中国通胀序列见步骤台账的序列面;无成分/权重数据,禁作成分归因。
  - 竞争性解释1: 供给侧/上游成本推动(【假设】):若为上游价格驱动,PPI先于CPI转正且幅度差大、CPI温和——与观察一致但缺进口价格序列佐证
  - 竞争性解释2: 内需边际修复(【假设】):若需求修复,PMI同比维度应同步改善——已观察到,但PMI水平仍低于荣枯线,需求证据弱
  - 竞争性解释3: 低基数效应(【假设】):同比口径受基期影响,若为基数主导,水平序列环比动能应平淡——可用PPI环比口径复核,现以同比空间呈现
  - 证据: CN_PMI_MFG@2026-10-01
- **机制链 M1_reflation_discount_shock**: 
  - E1 通胀再加速可核:美国CPI同比(派生)2026-02为2.434、2026-05为4.1666;核心CPI同比2026-05为2.8229、2026-08回落至2.4462;核心PCE同比最新3.12——再通胀集中于标题口径,核心口径温和 [证据: CPI@2026-10-01, CORE_CPI@2026-10-01, CORE_PCE@2026-09-01]
  - E1 政策再定价可核:Fed有效基金利率DFF年中下行(2026-08-20为3.63)后于2026-11-18回到3.88,目标区间上限DFEDTARU最新4.0;ECB存款便利利率2026-06-11与2026-09-10各上调25bp至2.5;日本政策利率(月均)2026-04为0.727、2026-07为0.978、2026-10为1.227;中国OMO利率三锚不变——政策阵营分裂 [证据: DFF@2026-11-18, DFEDTARU@2026-11-19, ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01]
  - E1 长端分解可核:十年期美债名义一年+95bp=实际TIPS_10Y+103bp+盈亏平衡BEI_10Y-8bp(共同交易日窗2025-11-18→2026-11-18);近一月名义-8bp=实际+8bp+盈亏平衡-16bp——抬升由实际利率主导,通胀预期锚定 [证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19]
  - E1 资产端可核:近一月(2026-10-21→最新)SPX -7.49%、NIKKEI225 -12.67%、GOLD_F -12.58%、SHCOMP -4.83%、DAX +0.36%,VIX +70.5%、DXY +2.12%、USDJPY +0.85%;HY_OAS 3.47pp未显著走阔——股金双跌、美元走强、信用平稳 [证据: SPX@2026-11-19, NIKKEI225@2026-11-20, GOLD_F@2026-11-19, SHCOMP@2026-11-20, DAX@2026-11-18, VIX@2026-11-19, DXY@2026-11-19, USDJPY@2026-11-19, HY_OAS@2026-11-18]
  - E2 机制环节:实际利率抬升→折现率上升→压制长久期权益与无息黄金;信用利差未走阔→本轮下跌非信用收缩事件。本引擎无期限溢价/股权风险溢价分解序列,该环拆分为【假设】 [缺失环: 缺期限溢价与股权风险溢价序列,折现率机制的定量拆分为【假设】,可由HY_OAS与CCC_OAS后续走向部分监视]
- **机制链 M2_japan_carry_competing**: 
  - E1 日本面可核:政策利率(月均)自2025-10的0.477升至2026-10的1.227;东京CPI同比2026-09为2.69再加速;全国CPI同比2026-10为2.44;USDJPY最新159.61(近一月+0.85%,日元未升值) [证据: JP_POLICY_RATE@2026-10-01, JP_CPI_YOY@2026-10-01, USDJPY@2026-11-19]
  - E3 套息平仓叙事:日央行加息→日元融资头寸去杠杆→全球风险资产波动传染——整环为【假设】:本引擎无套息头寸/持仓/杠杆数据,且汇率面(USDJPY微升)不支持平仓主导 [证伪指标: USDJPY]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN1_baseline_reflation_persists**()
  - 情景: 【假设非预测】基准情景:再通胀持续性高于预期,美欧日政策利率维持高位或续升,实际利率TIPS_10Y居高,中国维持低利率——增长温和、通胀回落缓慢。
  - 资产方向判断: 权益(SPX/NIKKEI225)与黄金GOLD_F承压(看跌),美元DXY偏强(看涨),信用利差HY_OAS温和走阔但不至危机(置信: 有历史相似证据) 
  - 敏感变量: TIPS_10Y, CPI
  - 证伪指标: CORE_CPI 阈值 美国核心CPI同比(派生口径)回落至2.0以下且连续两月——通胀快速消退则本情景证伪
  - 触发条件: TIPS_10Y维持≥2.8%且CPI同比(派生)≥3.5%再持续三个月(时限 2027-02-28)
- **SCN2_counter_inflation_fades**()
  - 情景: 【假设非预测】反例情景:供给冲击消退,美国标题通胀向核心收敛并快速回落,央行转鸽(先Fed后ECB),日本正常化继续但速度放缓。
  - 资产方向判断: 风险资产修复(看涨SPX/NIKKEI225),黄金先抑后扬(看涨,12个月维度),美元回落(看跌DXY)(置信: 有历史相似证据) 
  - 敏感变量: BEI_10Y, CORE_CPI
  - 证伪指标: BEI_10Y 阈值 BEI_10Y升破2.6且TIPS_10Y≥3.0连续两月——通胀预期脱锚+实际利率续高则本情景证伪
  - 触发条件: CORE_CPI同比(派生)连续两月≥2.4且BEI_10Y≥2.4(时限 2027-02-28)

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
- snapshot_fact:EA_HICP_YOY@2025-12-01 → EA_HICP_YOY
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

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、DFEDTARU、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、EA_HICP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
