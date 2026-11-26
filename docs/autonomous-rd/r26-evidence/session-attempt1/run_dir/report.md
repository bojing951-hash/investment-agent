# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261120T115457Z @ None
- 快照: research_snapshot_20261120 (target 20261120)
- 数据门(gate_a): 51/51 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-20、3个月前@2026-08-20、最新一期@2026-11-20 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 14 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_CPI_YOY(缺什么: CN_CPI_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_PPI_YOY(缺什么: CN_PPI_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_LPR_1Y(缺什么: CN_LPR_1Y(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_HICP_YOY(缺什么: EA_HICP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_YOY(缺什么: JP_CPI_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_TOKYO_YOY(缺什么: JP_CPI_TOKYO_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过

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
- SHCOMP = 3577.6174 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-19]
- HSI = 22841.62 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-19]
- CN_LPR_1Y = 3.0 percent @2026-10-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-10-20]
- CN_CPI_YOY = 0.7 percent @2026-10-31 [质量:WARN] [来源:snapshot_fact:CN_CPI_YOY@2026-10-31]
- CN_PPI_YOY = 5.7 percent @2026-10-31 [质量:WARN] [来源:snapshot_fact:CN_PPI_YOY@2026-10-31]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- DFF = 3.88 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:DFF@2026-11-18]
- DFEDTARU = 4.0 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:DFEDTARU@2026-11-19]
- NIKKEI225 = 59444.21 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-19]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 1.9 percent @2025-12-01 [质量:DEGRADED] [来源:snapshot_fact:EA_HICP_YOY@2025-12-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CON-1**: 过去一年美债长端收益率上行主要由实际利率分量而非通胀预期分量驱动;近一月盈亏平衡通胀回落与名义利率回落并存。
  - 依据: 引擎共同交易日三利率分解(us_rates_trio 面):十二个月窗名义上行的量级几乎全部由实际利率分量贡献,盈亏平衡分量为负;近一月窗名义回落的同时实际利率仍在上行、盈亏平衡快速回落。归档强渠道支持名义-实际同动读法(通胀保值债券与名义美债的日度变化相关系数为强正,E1,QB-20261110-022)。
  - 竞争性解释1: 主解释(实际利率驱动):央行再收紧叠加增长韧性推高实际利率,长端是实际利率现象——与名义-实际强共动边一致(E1)
  - 竞争性解释2: 竞争解释A(期限溢价/财政供给驱动):长端上行源于债券供给与期限溢价,与货币政策无关——本引擎无期限溢价序列,该环【假设】不可验
  - 竞争性解释3: 竞争解释B(通胀预期驱动):盈亏平衡应主导长端——但十二个月窗盈亏平衡分量为负,量级上数据不支持该解释成立
  - 证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19
- **CON-2**: 近一月美日中股市回调与波动急升、美元走强、黄金大跌并存(欧元区股指逆势上行);风险偏好收缩是数据支持最充分的统一解释。
  - 依据: 近一月波动率指数与股指反向共动、美元指数上行与黄金回落同现(引擎月窗资产面);归档强渠道:波动率与股指、股指与高收益利差均为强负共动,美元指数与黄金期货亦为归档负相关渠道(数值与窗见机制链 M1 第 4 环,均 E1,QB-20261110-022);CCC 级利差绝对水平高企。
  - 竞争性解释1: 主解释(风险偏好/美元流动性渠道):波动升→股指与信用承压,美元流动性收紧→黄金承压——与三条强渠道符号一致(E1)
  - 竞争性解释2: 竞争解释A(增长担忧渠道):若衰退担忧主导,长端利率应大幅下行而波动不必领涨——但十年期美债近一月仅小幅回落、工业生产同比走强、失业率平稳,增长数据暂不支持
  - 竞争性解释3: 竞争解释B(黄金独立定价:通胀预期回落驱动):盈亏平衡近一月确有回落,但黄金×盈亏平衡渠道在本地数据近零(r=+0.0255,E1 归档),通胀预期渠道不支持作方向依据
  - 证据: VIX@2026-11-19, SPX@2026-11-19, GOLD_F@2026-11-19, DXY@2026-11-19, CCC_OAS@2026-11-18, UST_10Y@2026-11-18
- **CON-3**: 日本无担保隔夜拆借利率最新月均为 1.227%,十二个月大幅正常化,而日元兑美元仍处弱势——教科书利差渠道(变化量口径)在本地数据近零,不能作为日元走势的方向依据(利差水平机制本引擎不可验)。
  - 依据: 引擎月均口径序列显示日本隔夜利率自上年前值持续抬升至最新 1.227%;而美元兑日元处于高位。归档边:美元兑日元分别与美债长端、短端利率的日度变化相关系数均近零,波动率与美元兑日元的相关系数亦近零(均近零渠道,E1,QB-20261110-022)——利率渠道与风险偏好→carry 渠道两条教科书链均被本地数据拒绝作方向依据。
  - 竞争性解释1: 主解释(渠道近零=放弃单因子叙事):日元驱动应按多因子观察,任何单一利率渠道在本地数据均不支持——数据保守读法
  - 竞争性解释2: 竞争解释A(利差水平而非变化主导):利差绝对水平仍大,正常化的变化量级不足以扭转方向——与近零相关并不矛盾,但水平机制本引擎无法验证【尚未验证】
  - 竞争性解释3: 竞争解释B(结构性资本流出驱动):日元弱势由流量(并购/再配置)而非价格驱动——无在册序列,【假设】
  - 证据: JP_POLICY_RATE@2026-10-01, USDJPY@2026-11-19
- **CON-4**: 中国出现工厂通胀高企与消费通胀低迷并存的剪刀差:中国PPI同比 5.7%,中国CPI同比 0.7%。
  - 依据: 两点值均为 2026-10-31 快照单点(历史序列不可得,检索范围=快照 series_store+注册表采集档通道,不可作趋势断言);制造业PMI 同比年内转正但绝对水平仍处荣枯线下方(49.3,2026-10)——修复与剪刀差并存。
  - 竞争性解释1: 主解释(成本冲击未传导至消费端):上游价格由供给与外需驱动,国内消费需求偏弱吸收不足——【推断】
  - 竞争性解释2: 竞争解释A(内需疲弱主导):CPI 低迷是主信号,PPI 高企由外部大宗与出口需求驱动,内需不足与 PMI 偏弱一致
  - 竞争性解释3: 竞争解释B(基数/口径效应):单月剪刀差可能是基数错位——单点数据无法排除,须历史序列验证【尚未验证】
  - 证据: CN_PPI_YOY@2026-10-31, CN_CPI_YOY@2026-10-31, CN_PMI_MFG@2026-10-01
- **机制链 M1**: 通胀再加速→政策再收紧→实际利率上行→风险偏好收缩
  - E1 始发冲击:美国CPI同比自 2026-02 低点至 2026-05 急升(引擎转折候选面 2.434→4.1666,同比空间),核心PCE同比三锚点连升(2.85→3.04→3.12)——通胀再加速 [证据: CPI@2026-10-01, CORE_PCE@2026-09-01]
  - E1 通胀-政策历史共动(CORE_PCE×FED_FUNDS 月网格 r=+0.422,归档边 COREPCE-FEDFUNDS,E1):政策再收紧落地——美联储 2026-09-16 决议加息(上限 3.75→4.0,次日生效),欧央行 2026-06-11 与 2026-09-10 两度决议加息(存款便利 2.0→2.5) [证据: DFEDTARU@2026-11-19, ECB_DFR@2026-09-16]
  - E1 名义-实际利率同动(r=+0.8278,归档边 TIPS10Y-UST10Y,E1):十年期美债十二个月 +95bp 中实际利率 +103bp、盈亏平衡 -8bp(共同交易日窗 2025-11-18→2026-11-18)——紧缩主要落在实际利率而非通胀预期 [证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19]
  - E1 风险偏好内环与美元-黄金渠道(VIX×SPX r=-0.7138、SPX×HY_OAS r=-0.6318、DXY×GOLD_F r=-0.3935,均 E1 归档强渠道):近一月 SPX -6.96%、VIX +64.3%、DXY +2.17%、GOLD_F -12.42%(引擎月窗 2026-10-20→2026-11-19)与该结构方向一致 [证据: VIX@2026-11-19, SPX@2026-11-19, HY_OAS@2026-11-18, DXY@2026-11-19, GOLD_F@2026-11-19]
  - E2 机制分辨:『实际利率→股指估值』的直接久期渠道在本地数据近零(NDX×UST_10Y r=+0.0586,归档近零渠道档)——第 4 环联动更可能经由风险偏好内环而非久期渠道;该分辨含推断成分 [缺失环: 本引擎无估值-利率因果序列,『经由风险偏好而非久期』的机制分辨含【假设】成分,仅以两条渠道的相关差为据]
- **机制链 M2**: 全球政策同步簇与日本正常化的传导
  - E1 日本无担保隔夜拆借月均十二个月 +0.75 个百分点(0.477→1.227),节奏为四地最快;转折窗 2026-04→2026-07(0.727→0.978) [证据: JP_POLICY_RATE@2026-10-01]
  - E1 政策事件簇(引擎 policy_event_clusters):欧央行 2026-06-11 决议 +25bp(6-17 生效)、2026-09-10 决议 +25bp(9-16 生效);美联储 2026-09-16 决议 +25bp(9-17 生效)——九月欧美决议日落在 ±7 日窗内,构成同一全球政策事件(POLCLUSTER-03,跨国产合并计数) [证据: ECB_DFR@2026-09-16, DFEDTARU@2026-11-19]
  - E3 日本加息向日元的传导:变化量口径下教科书利差渠道在本地数据近零(USDJPY×UST_10Y r=+0.0313、×UST_2Y r=+0.0064、VIX×USDJPY r=-0.0238,E1 近零档)——不能以该渠道作为日元走势的方向依据(日元弱势 USDJPY 159.61 另有驱动);利差水平机制与替代机制(贸易条件/资本流)本引擎无序列可验 [证伪指标: USDJPY]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**(基准情景)
  - 情景: 【假设非预测】美国通胀顽固:核心通胀维持当前区带上方,美联储将目标区间上限维持在 4.0%、实际利率续处高位,金融条件难松
  - 资产方向判断: 美股承压、高波动延续,高收益与 CCC 级信用利差走阔风险(置信: 有相关证据) 风险偏好内环(VIX×SPX r=-0.7138、SPX×HY_OAS r=-0.6318,E1)下,波动高位与股指弱势、信用走阔同现的结构延续概率较高——相关证据支持方向,非因果,非预测
  - 敏感变量: VIX, CORE_PCE
  - 证伪指标: CPI 阈值 美国CPI同比(引擎派生口径)连续两个月回落至 3.0% 以下——通胀顽固假设被证伪
  - 触发条件: 2027-02-15 前发布的最近一期 CPI 同比仍在 3.5% 或以上(紧缩延续条件成立)(时限 2027-02-15)
- **SCN-B**(反例情景)
  - 情景: 【假设非预测】通胀回落+政策转松:供给扰动消退带动通胀回落,美联储重启降息,实际利率见顶回落(近一月盈亏平衡 -16bp 与名义 -8bp 的组合若延续为趋势)
  - 资产方向判断: 美股修复上行,黄金再度走强(置信: 有历史相似证据) 历史相似段事后记录(analog 事后块,历史记录非预测):2023-10 簇事后十二个月 SPX +36.04%、GOLD_F +37.86%;2025-03 簇事后十二个月 SPX +16.33%、GOLD_F +48.83%——且 TOP-N 三个月窗方向分歧(符号一致率 0.6),外推须降级
  - 敏感变量: BEI_10Y, TIPS_10Y
  - 证伪指标: TIPS_10Y 阈值 TIPS_10Y 收盘升破 3.20%——实际利率再上新台阶,『通胀回落+利率见顶』假设被证伪
  - 触发条件: 2027-06-30 前 TIPS_10Y 回落至 2.60% 以下且 BEI_10Y 回升至 2.00% 以上(转松组合成立)(时限 2027-06-30)

## 语义审查(席位已裁)

- 席位裁决: REVISE(档: audit/semantic_review/20261120/VERDICT-20261120T115457Z-01.json)

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
- [OK |语义✔] S4_history_DFEDTARU 
- [OK |语义✔] S4_history_DFF 
- [OK |语义✔] S4_history_CN_PMI_MFG 
- [SKIP|—] S4_history_CN_CPI_YOY 地图计划指标 CN_CPI_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_PPI_YOY 地图计划指标 CN_PPI_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_POLICY_OVERNIGHT 地图计划指标 CN_POLICY_OVERNIGHT 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_OMO_7D 地图计划指标 CN_OMO_7D 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_LPR_1Y 地图计划指标 CN_LPR_1Y 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_EA_REAL_GDP_YOY 地图计划指标 EA_REAL_GDP_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_EA_HICP_YOY 地图计划指标 EA_HICP_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [OK |语义✔] S4_history_ECB_MRO 
- [OK |语义✔] S4_history_ECB_DFR 
- [SKIP|—] S4_history_JP_REAL_GDP_YOY 地图计划指标 JP_REAL_GDP_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_JP_CPI_YOY 地图计划指标 JP_CPI_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_JP_CPI_TOKYO_YOY 地图计划指标 JP_CPI_TOKYO_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
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

## 证据索引(71 行)

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
- snapshot_fact:SHCOMP@2026-11-19 → SHCOMP
- snapshot_fact:HSI@2026-11-19 → HSI
- snapshot_fact:CN_LPR_1Y@2026-10-20 → CN_LPR_1Y
- snapshot_fact:CN_CPI_YOY@2026-10-31 → CN_CPI_YOY
- snapshot_fact:CN_PPI_YOY@2026-10-31 → CN_PPI_YOY
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:DFF@2026-11-18 → DFF
- snapshot_fact:DFEDTARU@2026-11-19 → DFEDTARU
- snapshot_fact:NIKKEI225@2026-11-19 → NIKKEI225
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2025-12-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-19 → SZCI
- s3_envelope:CHINEXT@2026-11-19 → CHINEXT
- s3_envelope:HSCEI@2026-11-19 → HSCEI
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

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_CPI_YOY、CN_PPI_YOY、CN_POLICY_OVERNIGHT、CN_OMO_7D、CN_LPR_1Y、EA_REAL_GDP_YOY、EA_HICP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY、JP_CPI_YOY、JP_CPI_TOKYO_YOY
